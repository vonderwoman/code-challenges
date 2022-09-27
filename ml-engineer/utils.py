import os
import typing
from pathlib import Path
import pyarrow
import pyarrow.parquet as pq
from google.cloud import bigquery as bq
from google.cloud import bigquery_storage as bqs
from google.cloud.bigquery_storage_v1 import reader as bqs_reader


def _table_path(data_dir: str, table_name: str, suffix: str = 'parquet') -> str:
    return os.path.join(data_dir, f"{table_name}.{suffix}")


def bq_reader(
    bqrc: bqs.BigQueryReadClient,
    table,
    *,
    selected_fields: typing.Sequence[str] = [],
    row_restriction: str | None = None,
) -> tuple[bqs_reader.ReadRowsStream, bqs.types.ReadSession]:
    """
    Create a BigQuery Storage API Read Session for the given `table`

    Parameters:
      table: Fully Qualified name of table to read
      selected_fields: see :attr:`google.cloud.bigquery_storage_v1.types.ReadSession.TableReadOptions.selected_fields`
      row_restriction: see :attr:`google.cloud.bigquery_storage_v1.types.ReadSession.TableReadOptions.row_restriction`

    Returns:
      :class:`google.cloud.bigquery_storage_v1.reader.ReadRowsStream` or a list of :class:`google.cloud.bigquery_storage_v1.reader.ReadRowsStream` when max_stream_count > 1 and :class:`google.cloud.bigquery_storage_v1.types.ReadSession`
    """
    table = bq.table.TableReference.from_string(table)
    sess_req = bqs.types.ReadSession()
    sess_req.table = (
        f"projects/{table.project}/datasets/{table.dataset_id}/tables/{table.table_id}"
    )
    sess_req.data_format = bqs.types.DataFormat.ARROW
    if selected_fields:
        sess_req.read_options.selected_fields.extend(selected_fields)
    if row_restriction is not None:
        sess_req.read_options.row_restriction = row_restriction
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
    bqrc: bqs.BigQueryReadClient,
    table: str,
    data_dir: str,
    row_restriction: str | None = None,
    metadata: dict[str, str] = {},
) -> None:
    """
    Fetch a table from BigQuery and store it in parquet format in data_dir.

    Parameters:
      row_restriction: see :attr:`google.cloud.bigquery_storage.types.ReadSession.TableReadOptions.row_restriction`
    """
    reader, session = bq_reader(bqrc, table, row_restriction=row_restriction)
    pqf: pq.ParquetWriter = None
    try:
        for page in reader.rows(session).pages:
            batch = page.to_arrow()
            if pqf is None:
                downloaded_file = Path(_table_path(data_dir, table))
                downloaded_file.parent.mkdir(parents=True, exist_ok=True)
                schema = batch.schema.with_metadata(
                    {k.encode(): v.encode() for k, v in metadata.items()}
                )
                pqf = pq.ParquetWriter(downloaded_file, schema)
            pqf.write_table(pyarrow.Table.from_batches([batch]))
    finally:
        if pqf is not None:
            pqf.close()
    if pqf is None:
        raise Exception(
            f"Couldn't download data from {table}. Entities might be filtered out by row_restriction (train and eval split might be empty)."
        )


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 3:
        print(f'{sys.argv[0]} <fqdn_table> <data_dir>')
        sys.exit(1)

    table_to_parquet(bqs.BigQueryReadClient(), sys.argv[1], sys.argv[2])
