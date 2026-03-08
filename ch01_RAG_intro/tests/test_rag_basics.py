"""
Step-by-step tests for the ch01_RAG_intro/rag_basics.ipynb notebook.

Each test class mirrors one of the four labelled steps in the notebook:
  Step 1 – Text Chunking      (pure function, no external services)
  Step 2 – Embed and Store    (mocked OpenAI + ChromaDB)
  Step 3 – Retrieval          (mocked OpenAI + ChromaDB)
  Step 4 – Answer Generation  (mocked OpenAI)
"""

from pathlib import Path
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# Helpers – replicate the notebook functions exactly so every test exercises
# the real logic without importing the notebook itself.
# ---------------------------------------------------------------------------

def chunk_text(text, size=1000, overlap=200):
    """Split *text* into overlapping chunks (mirrors rag_basics.ipynb – Step 1).

    Uses ``max(end - overlap, start + 1)`` to guarantee forward progress and
    prevent an infinite loop when a break point falls inside the overlap zone.
    """
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            bp = text.rfind("\n\n", start, end)
            if bp == -1:
                bp = text.rfind(". ", start, end)
            if bp > start:
                end = bp + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = max(end - overlap, start + 1) if end < len(text) else end
    return chunks


def _embed_and_store(mock_client, chunks, db_path, collection_name):
    """Step 2 logic with an injectable OpenAI client (mirrors the notebook cell)."""
    import chromadb

    chroma = chromadb.PersistentClient(path=str(db_path))
    collection = chroma.get_or_create_collection(
        name=collection_name,
        metadata={"description": "Harry Potter knowledge base"},
    )

    embeddings = []
    for i in range(0, len(chunks), 100):
        batch = chunks[i:i + 100]
        res = mock_client.embeddings.create(model="text-embedding-3-small", input=batch)
        embeddings.extend([x.embedding for x in res.data])

    collection.add(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=embeddings,
        metadatas=[{"chunk_index": i} for i in range(len(chunks))],
    )
    return collection


def _retrieve(mock_client, collection, question, top_k=3):
    """Step 3 logic with injectable client/collection (mirrors the notebook cell)."""
    q_emb = mock_client.embeddings.create(
        model="text-embedding-3-small",
        input=question,
    ).data[0].embedding

    res = collection.query(
        query_embeddings=[q_emb],
        n_results=top_k,
        include=["documents"],
    )
    return res["documents"][0]


def _answer(mock_client, question, docs):
    """Step 4 logic with an injectable OpenAI client (mirrors the notebook cell)."""
    context = "\n\n---\n\n".join(docs)
    prompt = (
        "Answer the question using only the context below.\n\n"
        f"Context:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        "Answer:"
    )
    res = mock_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------

DATASETS_DIR = Path(__file__).parent.parent.parent / "datasets"
HARRY_POTTER_FILE = DATASETS_DIR / "text_files" / "harry_potter_knowledge_base.txt"


def _mock_embeddings_client(embeddings_list):
    """Return a MagicMock that acts as an OpenAI client returning *embeddings_list*."""
    client = MagicMock()
    result = MagicMock()
    result.data = [MagicMock(embedding=e) for e in embeddings_list]
    client.embeddings.create.return_value = result
    return client


def _mock_chat_client(answer_text):
    """Return a MagicMock that acts as an OpenAI client returning *answer_text*."""
    client = MagicMock()
    response = MagicMock()
    response.choices = [MagicMock(message=MagicMock(content=answer_text))]
    client.chat.completions.create.return_value = response
    return client


# ===========================================================================
# Step 1 – Text Chunking
# ===========================================================================

class TestStep1TextChunking:
    """Tests for Step 1: chunk_text function."""

    def test_short_text_returns_single_chunk(self):
        chunks = chunk_text("Hello world")
        assert len(chunks) == 1
        assert chunks[0] == "Hello world"

    def test_empty_string_returns_no_chunks(self):
        assert chunk_text("") == []

    def test_chunks_do_not_exceed_size(self):
        text = "a" * 5000
        for chunk in chunk_text(text, size=1000, overlap=200):
            assert len(chunk) <= 1000

    def test_long_text_produces_multiple_chunks(self):
        text = " ".join(["word"] * 2000)
        chunks = chunk_text(text, size=500, overlap=100)
        assert len(chunks) > 1

    def test_all_chunks_are_nonempty_strings(self):
        text = "First sentence. Second sentence. Third sentence."
        for chunk in chunk_text(text, size=20, overlap=5):
            assert isinstance(chunk, str)
            assert len(chunk.strip()) > 0

    def test_always_terminates_when_break_inside_overlap_zone(self):
        """chunk_text must not loop forever when a sentence break falls inside
        the overlap window (regression test for the start-advance guard)."""
        # Construct text where the only ". " occurs at index 14, which with
        # overlap=5 would cause start = 15 - 5 = 10 without the guard.
        text = "First sentence. " + "x" * 1000
        chunks = chunk_text(text, size=20, overlap=5)
        assert len(chunks) > 0

    def test_prefers_paragraph_break_over_mid_word_split(self):
        paragraph_a = "A" * 400
        paragraph_b = "B" * 400
        text = paragraph_a + "\n\n" + paragraph_b
        chunks = chunk_text(text, size=500, overlap=50)
        # The paragraph break must appear at a chunk boundary.
        joined = "\n\n".join(chunks)
        assert paragraph_a in joined
        assert paragraph_b in joined

    def test_harry_potter_file_chunked_successfully(self):
        text = HARRY_POTTER_FILE.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        assert len(chunks) > 0
        for chunk in chunks:
            assert isinstance(chunk, str)
            assert chunk.strip()


# ===========================================================================
# Step 2 – Embed and Store in ChromaDB
# ===========================================================================

class TestStep2EmbedAndStore:
    """Tests for Step 2: embed_and_store logic (OpenAI + ChromaDB mocked)."""

    def test_openai_embedding_api_called_once_for_small_batch(self, tmp_path):
        chunks = ["alpha", "beta", "gamma"]
        mock_client = _mock_embeddings_client([[0.1] * 5] * len(chunks))

        with patch("chromadb.PersistentClient") as mock_chroma:
            mock_collection = MagicMock()
            mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
            _embed_and_store(mock_client, chunks, tmp_path / "db", "col")

        mock_client.embeddings.create.assert_called_once()

    def test_collection_add_called_once(self, tmp_path):
        chunks = ["x", "y"]
        mock_client = _mock_embeddings_client([[0.0] * 3] * len(chunks))

        with patch("chromadb.PersistentClient") as mock_chroma:
            mock_collection = MagicMock()
            mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
            _embed_and_store(mock_client, chunks, tmp_path / "db", "col")

        mock_collection.add.assert_called_once()

    def test_chunk_ids_match_order(self, tmp_path):
        chunks = ["first", "second", "third"]
        mock_client = _mock_embeddings_client([[0.0] * 3] * len(chunks))
        captured = {}

        with patch("chromadb.PersistentClient") as mock_chroma:
            mock_collection = MagicMock()
            mock_collection.add.side_effect = lambda **kw: captured.update(kw)
            mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
            _embed_and_store(mock_client, chunks, tmp_path / "db", "col")

        assert captured["ids"] == ["chunk_0", "chunk_1", "chunk_2"]

    def test_documents_stored_match_input_chunks(self, tmp_path):
        chunks = ["doc one", "doc two"]
        mock_client = _mock_embeddings_client([[0.0] * 3] * len(chunks))
        captured = {}

        with patch("chromadb.PersistentClient") as mock_chroma:
            mock_collection = MagicMock()
            mock_collection.add.side_effect = lambda **kw: captured.update(kw)
            mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
            _embed_and_store(mock_client, chunks, tmp_path / "db", "col")

        assert captured["documents"] == chunks

    def test_embeddings_count_matches_chunks(self, tmp_path):
        chunks = ["a", "b", "c", "d"]
        mock_client = _mock_embeddings_client([[0.1] * 4] * len(chunks))
        captured = {}

        with patch("chromadb.PersistentClient") as mock_chroma:
            mock_collection = MagicMock()
            mock_collection.add.side_effect = lambda **kw: captured.update(kw)
            mock_chroma.return_value.get_or_create_collection.return_value = mock_collection
            _embed_and_store(mock_client, chunks, tmp_path / "db", "col")

        assert len(captured["embeddings"]) == len(chunks)


# ===========================================================================
# Step 3 – Retrieval
# ===========================================================================

class TestStep3Retrieval:
    """Tests for Step 3: retrieve logic (OpenAI + ChromaDB mocked)."""

    def test_returns_top_k_documents(self):
        docs = ["doc1", "doc2", "doc3"]
        mock_client = _mock_embeddings_client([[0.1] * 5])
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [docs]}

        result = _retrieve(mock_client, mock_collection, "Who is Harry?", top_k=3)

        assert result == docs

    def test_query_uses_question_embedding(self):
        embedding = [0.42] * 8
        mock_client = _mock_embeddings_client([embedding])
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [["result"]]}

        _retrieve(mock_client, mock_collection, "question text")

        call_kwargs = mock_collection.query.call_args.kwargs
        assert call_kwargs["query_embeddings"] == [embedding]

    def test_query_requests_correct_n_results(self):
        mock_client = _mock_embeddings_client([[0.0] * 5])
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [["a", "b"]]}

        _retrieve(mock_client, mock_collection, "q?", top_k=2)

        call_kwargs = mock_collection.query.call_args.kwargs
        assert call_kwargs["n_results"] == 2

    def test_openai_embedding_called_with_question(self):
        mock_client = _mock_embeddings_client([[0.0] * 5])
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [["result"]]}
        question = "Why did Dumbledore trust Snape?"

        _retrieve(mock_client, mock_collection, question)

        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small",
            input=question,
        )


# ===========================================================================
# Step 4 – Answer Generation
# ===========================================================================

class TestStep4Generation:
    """Tests for Step 4: answer generation logic (OpenAI mocked)."""

    def test_returns_llm_answer_text(self):
        expected = "Harry Potter is a famous wizard."
        mock_client = _mock_chat_client(expected)

        result = _answer(mock_client, "Who is Harry Potter?", ["He is a wizard."])

        assert result == expected

    def test_docs_joined_with_separator_in_prompt(self):
        mock_client = _mock_chat_client("ok")
        docs = ["Part A", "Part B"]

        _answer(mock_client, "Q?", docs)

        sent = mock_client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
        assert "Part A\n\n---\n\nPart B" in sent

    def test_question_included_in_prompt(self):
        mock_client = _mock_chat_client("ok")
        question = "What is the Philosopher's Stone?"

        _answer(mock_client, question, ["Some context."])

        sent = mock_client.chat.completions.create.call_args.kwargs["messages"][0]["content"]
        assert question in sent

    def test_chat_completions_called_once(self):
        mock_client = _mock_chat_client("answer")

        _answer(mock_client, "Q?", ["context"])

        mock_client.chat.completions.create.assert_called_once()
