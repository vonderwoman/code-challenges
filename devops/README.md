# 7Learnings DevOps Code Challenges

The 7Learnings code challenge is an opportunity to demonstrate proficiency in the problem solving skills we expect you to use at 7Learnings.

## Coding environment

At 7Learnings, we use Python 3.10 as the main coding language. So it's strongly encourage to create isolated Python using [virtualenv](https://virtualenv.pypa.io/en/latest/) to prepare yourself for the following challenges.

```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

We also provide a helper function (`table_to_parquet`) in the `utils.py` to let you focus on the challenges. But feel free to change it if you find a better way to do it. You can find example code below.

```python
from google.cloud import bigquery_storage as bqs
from utils import table_to_parquet

table_to_parquet(
    bqs.BigQueryReadClient(), "candidate-01-7l.devops.transactions", "downloaded_data"
)
```

## The Challenge

You are tasked to reduce the network bandwidth while downloading table data (parquet file) to the local storage. To give you a bit of context, the data scientists need to download the data from BigQuery tables to train/eval/test the machine learning models.
The data we have is often quite huge and it costs money on Google Cloud and take time to download all of them.  That's why we would like you to take deep inspection of our code or find a new way to save the network bandwidth.

Feel the task is too easy? We have a bonus task for you.
Before training models on that data, we need to load it fully into memory to perform shuffling and splitting into three different data splits (train/eval/test).
It would be nice if splitting and sorting by the `_data_split` and `_data_shuffle` columns would already happen when when writing to the parquet files, so we could stream it during model training.

#### Time Allotment

We respect your time and don't want you spending more 3 hours on your challenge. We just want to get a sense of your thought process and development patterns. If there are features you don't have time to implement, feel free to use pseudo code to describe the intended behavior.


## What We Review

Your code will be reviewed by our engineers. The aspects of your code we will judge include:

- ability to get the technical environment set up
- completion of tasks
- code cleanness
- reasoning of the solution

## Submission
Email a link to a repository with your implementation or zip file with your repository to your 7Learnings contact.

