# 7Learnings DevOps Code Challenges

The 7Learnings code challenge is an opportunity to demonstrate proficiency in the problem solving skills we expect you to use at 7Learnings.

## Coding environment

At 7Learnings, we use Python 3.10 as the main coding language. So it's strongly encouraged to create isolated Python environment using [virtualenv](https://virtualenv.pypa.io/en/latest/) to prepare yourself for the challenge.

First, create a python environment and install required packages:
```sh
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Include any additional dependencies you need in [requirements.txt](https://github.com/7Learnings/code-challenges/blob/f473d873dc9b83b786af702fa475c7dbeeee4b65/ml-engineer/requirements.txt).

Secondly, you will need to download synthetic transactions data for this assignment.
It is available in `.parquet` format under [https://storage.googleapis.com/candidate-01-7l-ml-engineer/transactions.parquet](https://storage.googleapis.com/candidate-01-7l-ml-engineer/transactions.parquet).
For convenience, save the file under the same folder as `pipeline.py`.

Please keep in mind that the table is relatively big, and you will need ~150MB of available space to store it locally.

## The Challenge

The challenge is to implement a "pipeline" command that prepares data for model training. 
It does so in two steps: `get-data` and `check-data`.
Example usage:
```
python pipeline.py get-data check-data
```

### Part 1
`get-data` loads transactions data (from the downloaded file) into memory. 

You will need to modify `get-data` step for the following tasks:

  1a. Table is relatively big with ~5 million rows. It contains train, evaluation and test datasets.
      Split parquet file into 3 separate (in-memory) datasets: train, eval, test. 
      Use `_data_split` column to determine which dataset the sample should correspond to.

  1b. Shuffle datasets according to `_data_shuffle` column in a reproducible way.
      Row order after shuffling needs to be the same between separate runs.

### Part 2
`check-data` makes sure that training and evaluation datasets are similarly distributed.
There is only one task to implement in this step:

  2. Compare distributions of features between train and eval datasets.
     Raise an error or display a warning if distributions are significantly different.

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
