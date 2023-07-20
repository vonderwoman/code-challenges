import csv
import hashlib
import itertools
import os
import random
import traceback
from base64 import b64decode
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from hmac import compare_digest
from typing import Annotated, Literal
from uuid import uuid4

import annotated_types
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.models import OAuthFlowClientCredentials, OAuthFlows
from fastapi.security import OAuth2
from google.cloud import storage as gcs  # type: ignore[attr-defined]
from jose import JWTError, jwt
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "e0155cc887f6683082812b8a546946f78bd80b29cfb9bf17090e2f4a57876ab0",
)
ALGORITHM = "HS256"
EXPIRE_MIN = 15

app = FastAPI()

oauth2_scheme = OAuth2(
    flows=OAuthFlows(
        clientCredentials=OAuthFlowClientCredentials(tokenUrl="/oauth2/v2.0/token")
    )
)


async def authenticate_client(
    credentials: Annotated[str, Depends(oauth2_scheme)]
) -> str:
    if compare_digest(
        credentials,
        "Basic MTQxNGRmMzEtY2MwYi00NmRiLTlmOWYtZmYxNzUyYWMyOThmOjZTSEJGaHVUVytvZVBmYlJvcEVkRSF6YzE=",
    ):
        return b64decode(credentials.removeprefix("Basic ")).split(b":", 1)[0].decode()
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect client credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


class AccessToken(BaseModel):
    access_token: str
    token_type: str


@app.post("/oauth2/v2.0/token")
async def authenticate(
    client_id: Annotated[str, Depends(authenticate_client)]
) -> AccessToken:
    access_token = jwt.encode(
        {
            "sub": client_id,
            "sid": str(uuid4()),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MIN),
        },
        SECRET_KEY,
        algorithm=ALGORITHM,
    )
    return AccessToken(access_token=access_token, token_type="Bearer")


# ==============================================================================
# Authenticated endpoints
# ------------------------------------------------------------------------------


class Session(BaseModel):
    client_id: str
    session_id: str


async def verify_session(token: str = Depends(oauth2_scheme)) -> Session:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token.removeprefix("Bearer "),
            SECRET_KEY,
            algorithms=[ALGORITHM],
            subject="1414df31-cc0b-46db-9f9f-ff1752ac298f",
        )
        if "sid" not in payload:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    return Session(client_id=payload["sub"], session_id=payload["sid"])


@app.get("/users/me/", description="Get back session info to test authentication")
async def get_client(session: Annotated[Session, Depends(verify_session)]) -> Session:
    return session


class Price(BaseModel):
    market: Literal["DE", "ES", "FR", "PL", "UK", "US"]
    channel: str
    price: Annotated[
        float, annotated_types.MultipleOf(Decimal("0.01")), annotated_types.Gt(0)
    ]
    valid_from: datetime
    valid_until: datetime


class ProductPrices(BaseModel):
    product_id: int
    prices: list[Price]


class ImportProductPricesIn(BaseModel):
    products: Annotated[list[ProductPrices], annotated_types.Len(max_length=1_000)]


class ImportProductPricesOut(BaseModel):
    num_imported: Annotated[int, annotated_types.Ge(0)]


@app.post(
    "/product-prices/",
    description="""
Import given prices into shop.

In order to provide backpressure, the shop system might import only up to the returned `num_imported` number of products.
Resubmit the remaining products with the next batch.
""",
)
async def post_product_prices(
    req: ImportProductPricesIn, session: Annotated[Session, Depends(verify_session)]
) -> ImportProductPricesOut:
    # backpressure
    products = req.products[0 : random.randint(0, 2 * len(req.products))]

    path = f"prices_{session.session_id}.csv"
    os.path.exists(path)

    # flatten uploaded prices into CSV
    with open("prices.csv") as f:
        r = csv.reader(f)
        fieldnames = next(r)
    with open(path, "a") as f:
        w = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        if f.tell() == 0:
            w.writeheader()
        for prod in products:
            row = prod.dict(exclude={"prices"})
            for price in prod.prices:
                row.update(price.dict())
                w.writerow(row)

    return ImportProductPricesOut(num_imported=len(products))


class Upload(BaseModel):
    url: str
    error: str | None


class ValidateProductPrices(BaseModel):
    first_50_products: Annotated[
        list[ProductPrices], annotated_types.Len(max_length=50)
    ]
    correct_checksum: bool
    gcs_upload: Upload


@app.get(
    "/validate-product-prices/",
    description="""
Read back alll imported product prices and validate your submission.
""",
)
async def get_product_prices(
    session: Annotated[Session, Depends(verify_session)]
) -> ValidateProductPrices:
    path = f"prices_{session.session_id}.csv"
    if not os.path.exists(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No uploaded prices found in this session {session}",
        )
    with open(path, "rb") as f:
        candidate = hashlib.file_digest(f, "sha256").hexdigest()
    with open("prices.csv", "rb") as f:
        expectation = hashlib.file_digest(f, "sha256").hexdigest()
    correct_checksum = compare_digest(expectation, candidate)

    price_keys = Price.schema()["properties"].keys()
    products: dict[int, list[Price]] = {}
    with open(path) as f:
        # nested prices for API response
        for row in csv.DictReader(f):
            price = Price.model_validate({k: row.pop(k) for k in price_keys})
            products.setdefault(
                ProductPrices.model_validate({"prices": [], **row}).product_id, []
            ).append(price)

    # use validation to export the local copy (relying on session affinity to correctly assemble the csv on local filesystem)
    gcs_url = f"gs://candidate-01-7l-api-backend/submissions/{path}"
    try:
        gcs.Blob.from_string(gcs_url, client=gcs.Client()).upload_from_filename(path)
        gcs_upload_error = None
    except Exception as e:
        gcs_upload_error = "".join(
            traceback.format_exception(type(e), e, e.__traceback__)
        )

    return ValidateProductPrices(
        first_50_products=[
            ProductPrices(product_id=product_id, prices=prices)
            for product_id, prices in itertools.islice(products.items(), 50)
        ],
        gcs_upload=Upload(url=gcs_url, error=gcs_upload_error),
        correct_checksum=correct_checksum,
    )
