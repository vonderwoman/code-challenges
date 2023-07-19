DOCKER ?= docker
PROJECT_ID := candidate-01-7l
SERVICE_NAME := api-backend
IMAGE_TAG := $(shell git describe --always --dirty --tags | tr '.' '-' | sed 's/[:\/]/-/g')
IMAGE_NAME := eu.gcr.io/$(PROJECT_ID)/$(SERVICE_NAME)
# use make BUILD_VER=2 to redeploy same image
BUILD_VER := 1
REVISION := $(IMAGE_TAG)-$(BUILD_VER)

CLOUD_RUN_ARGS = --region europe-west1 --platform managed

export CLOUDSDK_CORE_PROJECT=$(PROJECT_ID)

.DELETE_ON_ERROR:

.DEFAULT_GOAL := help

all: help

.PHONY: help
help:  # Show help
	@grep -H -E '^[0-9A-Za-z_-]+:\s*#.*$$' $(MAKEFILE_LIST) | sort | \
		awk -F ':' '{ gsub(/\s*#/, "", $$3); printf "\033[37;1m%-20s\033[0m %s\n", $$2, $$3 }'

.PHONY: serve
serve: # Serve for local development
	uvicorn main:app --reload --reload-dir .

.PHONY: build-image
build-image:  # Build deployment image
	@ # https://docs.docker.com/engine/reference/commandline/build/#specifying-external-cache-sources
	DOCKER_BUILDKIT=1 $(DOCKER) build --cache-from $(IMAGE_NAME) -t $(IMAGE_NAME):$(IMAGE_TAG) --build-arg BUILDKIT_INLINE_CACHE=1 --build-context api-backend=.. .

.PHONY: push-image
push-image:  # Publish deployment image
	@echo "[Image name]: $(IMAGE_NAME):$(IMAGE_TAG)"
	$(DOCKER) push $(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: push-latest
push-latest:  # Publish latest-$ENV tag
	@echo "[Image name]: $(IMAGE_NAME):latest-$(ENV)"
	$(DOCKER) tag $(IMAGE_NAME):$(IMAGE_TAG) $(IMAGE_NAME):latest
	$(DOCKER) push $(IMAGE_NAME):latest

run-image: build-image
run-image: # Run image locally
	$(DOCKER) run --net=host -it --rm $(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: deployment
deployment:
	@echo "Google Run service: $(SERVICE_NAME)"

# session-affinity for batch-wise upload to local file
	gcloud run deploy $(SERVICE_NAME) $(CLOUD_RUN_ARGS) \
		--image=$(IMAGE_NAME):$(IMAGE_TAG) \
		--revision-suffix=$(REVISION) \
		--service-account api-backend@candidate-01-7l.iam.gserviceaccount.com \
		--port 8000 \
		--timeout=5s \
		--max-instances 2 \
		--concurrency=50 \
		--cpu 1000m \
		--memory 256Mi \
		--session-affinity \
		--cpu-throttling \
		--allow-unauthenticated

# Keep last 3 revisions for rollback and pending requests
	gcloud run revisions list $(CLOUD_RUN_ARGS) \
		--sort-by=~creationTimestamp --format='value(name)' \
		--service $(SERVICE_NAME) | sed 1,3d | \
		xargs --no-run-if-empty -n 1 gcloud run revisions delete $(CLOUD_RUN_ARGS) --quiet
