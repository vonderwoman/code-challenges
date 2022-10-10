import sys
import pyarrow.parquet as pq


def get_data():
    # Prerequisite: download `transactions.parquet` from https://storage.googleapis.com/candidate-01-7l-ml-engineer/transactions.parquet
    data_source = pq.read_table("transactions.parquet")

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
