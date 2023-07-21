# 7Learnings API & backend Code Challenges

The 7Learnings code challenge is an opportunity to demonstrate proficiency in the problem solving skills we expect you to use at 7Learnings.

## Coding environment

At 7Learnings, we use Python 3.11 as the main coding language. So it's strongly encouraged to create isolated Python environment using [virtualenv](https://virtualenv.pypa.io/en/latest/) to prepare yourself for the challenge.

First, create a python environment and install required packages:

```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Include any additional dependencies you need in [requirements.txt](https://github.com/7Learnings/code-challenges/blob/3df21b78b54e33bbb2d592e814960938ed604bf1/api-backend/requirements.txt).

## The Challenge

The challenge is to finish the implementation of a shop integration to upload prices via an API.
Client usage:

```
python upload_prices.py credentials.json prices.csv
```

### [API server](https://api-backend-olsgyubl4a-ew.a.run.app)

- Use the [API docs](https://api-backend-olsgyubl4a-ew.a.run.app/docs/) for more detailed info.
- Also see [FastAPI](https://fastapi.tiangolo.com/) for more info on the server.

### Client (**to be implemented**)

1. Correctly authenticate with the API using `credentials.json`.
2. Upload all the prices from the given `prices.csv` to the `/product-prices` endpoint.
3. You can check `/validate-product-prices` to see if you upload was correct.

#### Time Allotment

We respect your time and don't want you spending more 3 hours on your challenge. We just want to get a sense of your thought process and development patterns. If there are features you don't have time to implement, feel free to use pseudo code to describe the intended behavior.

## What We Review

Your code will be reviewed by our engineers. The aspects of your code we will judge include:

- ability to get the technical environment set up
- completion of tasks
- code cleanness
- reasoning of the solution

## Submitting your results

1. Send us the us the `upload.gcs_url` from your final `/validate-product-prices` request.
2. Send us your final code, preferably as either one of the following:
   - git-bundle: `git bundle create my_changes.bundle origin/main..`
   - patches: `git format-patch origin/main..`
