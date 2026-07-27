from airflow.scripts.parse import clean_text

def test_clean_text_removes_scripts():
    result = clean_text("<script>alert('bad');</script>Apple Revenue was $100B")
    assert result == "Apple Revenue was $100B"
