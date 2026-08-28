from unittest.mock import mock_open, patch

import pytest
from airflow.scripts.parse import clean_text, parse_filing


# --- Unit Tests for Text Cleaning ---
@pytest.mark.parametrize("input_text, expected", [
    # Test 1: Basic Javascript scrubbing
    ("<script>alert('bad');</script>Apple Revenue was $100B", "Apple Revenue was $100B"),
    
    # Test 2: Multiline Javascript scrubbing (Edge case)
    ("<script>\nfunction test() { return 1; }\n</script>Net Income: 50M", "Net Income: 50M"),
    
    # Test 3: SEC Edgar artifacts like $('some_id')
    ("Revenue $('products') increased", "Revenue  increased"),
    
    # Test 4: Pure text shouldn't be altered
    ("No HTML here. Just text.", "No HTML here. Just text.")
])
def test_clean_text(input_text, expected):
    """
    Parametrized test to prove our regex cleaning handles standard, multiline,
    and Edgar-specific edge cases reliably in the CI/CD pipeline.
    """
    assert clean_text(input_text) == expected


# --- Mocked Integration Tests for Parsing ---
@patch("airflow.scripts.parse.partition_html")
@patch("builtins.open", new_callable=mock_open, read_data="<script>JS</script><html><body><p>Financial Data</p></body></html>")
def test_parse_filing_mocks_file_io(mock_file, mock_partition):
    """
    Tests the file reading and partitioning logic WITHOUT actually reading from disk.
    This is crucial for CI/CD so tests don't break if the raw data files are missing.
    """
    # Define what the mocked Unstructured partitioner should return
    mock_partition.return_value = ["Element1", "Element2"]
    
    # Run the function
    result = parse_filing("fake/path/to/10-K.txt")
    
    # Assertions
    mock_file.assert_called_once_with("fake/path/to/10-K.txt", "r", encoding="utf-8")
    mock_partition.assert_called_once()
    assert len(result) == 2
    assert result == ["Element1", "Element2"]
