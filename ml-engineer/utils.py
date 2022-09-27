import os
import typing
from pathlib import Path
import pyarrow
import pyarrow.parquet as pq
from google.cloud import bigquery as bq
from google.cloud import bigquery_storage as bqs
from google.cloud.bigquery_storage_v1 import reader as bqs_reader


def bq_reader(
    bqrc: bqs.BigQueryReadClient,
    table,
) -> tuple[bqs_reader.ReadRowsStream, bqs.types.ReadSession]:
    """
    Create a BigQuery Storage API Read Session for the given `table`

    Parameters:
      table: Fully Qualified name of table to read

    Returns:
      :class:`google.cloud.bigquery_storage_v1.reader.ReadRowsStream` or a list of :class:`google.cloud.bigquery_storage_v1.reader.ReadRowsStream` when max_stream_count > 1 and :class:`google.cloud.bigquery_storage_v1.types.ReadSession`
    """
    table = bq.table.TableReference.from_string(table)
    sess_req = bqs.types.ReadSession()
    sess_req.table = (
        f"projects/{table.project}/datasets/{table.dataset_id}/tables/{table.table_id}"
    )
    sess_req.data_format = bqs.types.DataFormat.ARROW
    sess_req.read_options.arrow_serialization_options.buffer_compression = (
        bqs.types.ArrowSerializationOptions.CompressionCodec.ZSTD
    )
    sess = bqrc.create_read_session(
        parent=f"projects/{table.project}",
        read_session=sess_req,
        max_stream_count=1,
    )
    if len(sess.streams) == 0:
        raise IndexError(f"No BQ storage API streams, {table} might be empty")
    return bqrc.read_rows(sess.streams[0].name), sess


def table_to_parquet(
    table: str,
    path: str | Path,
) -> None:
    """
    Fetch a table from BigQuery and store it in parquet format in data_dir.

    Parameters:
      row_restriction: see :attr:`google.cloud.bigquery_storage.types.ReadSession.TableReadOptions.row_restriction`
    """
    bqrc = bqs.BigQueryReadClient()
    reader, session = bq_reader(bqrc, table)
    pqf: pq.ParquetWriter = None
    try:
        for page in reader.rows(session).pages:
            batch = page.to_arrow()
            if pqf is None:
                downloaded_file = Path(path)
                downloaded_file.parent.mkdir(parents=True, exist_ok=True)
                pqf = pq.ParquetWriter(downloaded_file, batch.schema)
            pqf.write_table(pyarrow.Table.from_batches([batch]))
    finally:
        if pqf is not None:
            pqf.close()
    if pqf is None:
        raise Exception(
            f"Couldn't download data from {table}. Entities might be filtered out by row_restriction (train and eval split might be empty)."
        )
