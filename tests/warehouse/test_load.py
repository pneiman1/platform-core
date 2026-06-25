"""Unit tests for load_dataframe — verify the write_pandas call is built from our
conventions and that the auto_create_table / overwrite flags pass through."""
from unittest.mock import MagicMock, patch

import pandas as pd

from platform_core.warehouse.load import load_dataframe


@patch("platform_core.warehouse.load.write_pandas")
def test_defaults_auto_create_and_overwrite_true(mock_wp):
    mock_wp.return_value = (True, 1, 3, None)
    n = load_dataframe(
        MagicMock(), pd.DataFrame({"a": [1, 2, 3]}),
        table="t", schema="s", database="d",
    )
    assert n == 3
    kwargs = mock_wp.call_args.kwargs
    assert kwargs["auto_create_table"] is True
    assert kwargs["overwrite"] is True


@patch("platform_core.warehouse.load.write_pandas")
def test_auto_create_false_and_overwrite_false_passthrough(mock_wp):
    """The explicit-types ingestion path: append into a pre-created table."""
    mock_wp.return_value = (True, 1, 0, None)
    load_dataframe(
        MagicMock(), pd.DataFrame({"a": []}),
        table="t", schema="s", database="d",
        auto_create_table=False, overwrite=False,
    )
    kwargs = mock_wp.call_args.kwargs
    assert kwargs["auto_create_table"] is False
    assert kwargs["overwrite"] is False
    # tz fidelity is preserved regardless of the create mode.
    assert kwargs["use_logical_type"] is True


@patch("platform_core.warehouse.load.write_pandas")
def test_uppercases_columns_and_target(mock_wp):
    mock_wp.return_value = (True, 1, 1, None)
    load_dataframe(
        MagicMock(), pd.DataFrame({"lower": [1]}),
        table="my_table", schema="my_schema", database="d",
    )
    written_df = mock_wp.call_args.args[1]
    kwargs = mock_wp.call_args.kwargs
    assert list(written_df.columns) == ["LOWER"]
    assert kwargs["table_name"] == "MY_TABLE"
    assert kwargs["schema"] == "MY_SCHEMA"


@patch("platform_core.warehouse.load.write_pandas")
def test_raises_when_write_pandas_fails(mock_wp):
    mock_wp.return_value = (False, 0, 0, None)
    try:
        load_dataframe(MagicMock(), pd.DataFrame({"a": [1]}),
                       table="t", schema="s", database="d")
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected RuntimeError on write_pandas failure")
