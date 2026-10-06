from app.services.chunking import chunk_text, normalize_text


def test_normalize_text():
    assert normalize_text("  hello\nworld ") == "hello world"


def test_chunk_text_has_overlap_and_content():
    chunks = chunk_text("a" * 1000, chunk_size=300, overlap=50)
    assert len(chunks) == 4
    assert all(chunks)
