from packages.retrieval.chunking import chunk_text


def test_chunk_text_overlap() -> None:
    text = "A" * 500
    chunks = chunk_text("s1", text, chunk_size=200, overlap=20)
    assert len(chunks) >= 3
    assert chunks[0].source_id == "s1"
    assert chunks[1].text[:20] == chunks[0].text[-20:]
