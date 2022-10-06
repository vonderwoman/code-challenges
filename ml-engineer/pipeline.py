import sys
from utils import table_to_parquet
from google.cloud import bigquery_storage as bqs
from utils import table_to_parquet


def get_data():
    table_to_parquet('candidate-01-7l.data.ml_interview_transactions', 'transactions.parquet')
    # 1a. split parquet files by _data_split column

    # 1b. reproducible shuffling of data by precomputed _data_shuffle column


def check_data():
    # 2. warn about different distributions between train and eval splits
    pass


if __name__ == '__main__':
    if 'get-data' in sys.argv:
        get_data()
    if 'check-data' in sys.argv:
        check_data()
