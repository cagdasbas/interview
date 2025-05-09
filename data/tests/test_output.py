from unittest.mock import MagicMock, patch

import pytest

from tekmetric_data.output import DiskWriter, WriterRegistry, S3Writer


@patch("tekmetric_data.output.pq.ParquetWriter")
@patch("tekmetric_data.output.Path")
def test_disk_writer_write_and_close(mock_path, mock_parquet_writer):
    mock_schema = MagicMock()
    mock_output_dir = MagicMock()
    mock_file = MagicMock()
    mock_path.return_value = mock_output_dir
    mock_output_dir.__truediv__.return_value = mock_file
    mock_output_dir.exists.return_value = False
    mock_file.exists.return_value = False

    writer = DiskWriter(schema=mock_schema, output_dir="out", filename="file.parquet")
    data = MagicMock()
    writer.write(data)
    writer.close()
    mock_parquet_writer.assert_called_once_with(where=str(mock_file), schema=mock_schema)
    mock_parquet_writer.return_value.write.assert_called_once_with(data)
    mock_parquet_writer.return_value.close.assert_called_once()


def test_disk_writer_write_none_does_nothing():
    with patch("tekmetric_data.output.pq.ParquetWriter") as mock_parquet_writer, \
            patch("tekmetric_data.output.Path") as mock_path:
        mock_schema = MagicMock()
        mock_output_dir = MagicMock()
        mock_file = MagicMock()
        mock_path.return_value = mock_output_dir
        mock_output_dir.__truediv__.return_value = mock_file
        mock_output_dir.exists.return_value = True
        mock_file.exists.return_value = False

        writer = DiskWriter(schema=mock_schema, output_dir="out", filename="file.parquet")
        writer.write(None)
        mock_parquet_writer.return_value.write.assert_not_called()


def test_writer_factory_disk():
    writer = WriterRegistry.get("disk", schema="s", output_dir="o", filename="f")
    assert writer is not None
    assert writer.__class__.__name__ == "DiskWriter"


def test_s3_writer_write_and_close_raise():
    writer = S3Writer(schema="s", bucket_name="b", s3_client="c")
    with pytest.raises(NotImplementedError):
        writer.write("data")
    with pytest.raises(NotImplementedError):
        writer.close()


def test_writer_factory_s3_returns_s3writer():
    writer = WriterRegistry.get("s3", schema="s", bucket_name="b", s3_client="c")
    assert writer is not None
    assert writer.__class__.__name__ == "S3Writer"


def test_writer_factory_invalid_type():
    with pytest.raises(ValueError):
        WriterRegistry.get("unknown")
