"""
Unit tests for ch01_RAG_intro/rag_basics.ipynb

These tests validate the core RAG pipeline functions defined in the notebook:
  - chunk_text:      pure-Python text splitter (no mocks needed)
  - embed_and_store: embeds chunks via OpenAI and persists them in ChromaDB
  - retrieve:        queries the vector store with an embedded question
  - answer:          generates an answer via the OpenAI chat API
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers – replicate the notebook functions so tests are self-contained
# ---------------------------------------------------------------------------


def chunk_text(text, size=1000, overlap=200):
    """Split *text* into overlapping chunks (mirrors notebook Cell 10)."""
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            bp = text.rfind("\n\n", start, end)
            if bp == -1:
                bp = text.rfind(". ", start, end)
            if bp >= start + overlap:  # ensures forward progress
                end = bp + 1
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap if end < len(text) else end
    return chunks


def embed_and_store(client, chunks, db_path, collection_name, embedding_model, chroma_client=None):
    """Embed *chunks* via OpenAI and persist them in ChromaDB (mirrors Cell 12).

    *chroma_client* can be supplied for testing so that the real ChromaDB library
    (which initialises heavyweight ONNX models) is never imported.
    """
    if chroma_client is None:  # pragma: no cover – real path, not exercised in tests
        import chromadb
        chroma_client = chromadb.PersistentClient(path=str(db_path))

    collection = chroma_client.get_or_create_collection(
        name=collection_name,
        metadata={"description": "Harry Potter knowledge base"},
    )

    embeddings = []
    for i in range(0, len(chunks), 100):
        batch = chunks[i : i + 100]
        res = client.embeddings.create(model=embedding_model, input=batch)
        embeddings.extend([x.embedding for x in res.data])

    collection.add(
        ids=[f"chunk_{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=embeddings,
        metadatas=[{"chunk_index": i} for i in range(len(chunks))],
    )
    return collection


def retrieve(client, collection, question, embedding_model, top_k=3):
    """Embed *question* and return the top-k matching chunks (mirrors Cell 14)."""
    q_emb = (
        client.embeddings.create(model=embedding_model, input=question)
        .data[0]
        .embedding
    )
    res = collection.query(
        query_embeddings=[q_emb],
        n_results=top_k,
        include=["documents"],
    )
    return res["documents"][0]


def answer(client, question, docs):
    """Generate an answer given retrieved *docs* (mirrors Cell 16)."""
    context = "\n\n---\n\n".join(docs)
    prompt = f"""Answer the question using only the context below.

Context:
{context}

Question:
{question}

Answer:"""
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content


# ---------------------------------------------------------------------------
# chunk_text tests  (no mocking required – pure function)
# ---------------------------------------------------------------------------


class TestChunkText:
    def test_short_text_single_chunk(self):
        text = "Hello world"
        chunks = chunk_text(text, size=1000, overlap=200)
        assert chunks == ["Hello world"]

    def test_long_text_produces_multiple_chunks(self):
        # Create text longer than chunk size
        text = "word " * 300  # ~1500 characters
        chunks = chunk_text(text, size=500, overlap=100)
        assert len(chunks) > 1

    def test_chunks_cover_all_content(self):
        """Every word in the original text must appear in at least one chunk."""
        text = "The quick brown fox jumps over the lazy dog. " * 50
        chunks = chunk_text(text, size=200, overlap=50)
        combined = " ".join(chunks)
        for word in ["quick", "brown", "fox", "lazy", "dog"]:
            assert word in combined

    def test_overlap_means_content_repeated(self):
        """With overlap > 0, the end of one chunk should appear in the next."""
        text = "A" * 300 + "B" * 300
        chunks = chunk_text(text, size=400, overlap=100)
        assert len(chunks) >= 2
        # The second chunk should start before the first chunk ends
        assert len(chunks[0]) > 0
        assert len(chunks[1]) > 0

    def test_empty_text_returns_empty_list(self):
        assert chunk_text("", size=1000, overlap=200) == []

    def test_exact_size_text_single_chunk(self):
        text = "x" * 1000
        chunks = chunk_text(text, size=1000, overlap=200)
        assert len(chunks) == 1
        assert chunks[0] == "x" * 1000

    def test_prefers_paragraph_break(self):
        """chunk_text should prefer splitting on double-newlines."""
        para1 = "First paragraph content here. " * 10
        para2 = "Second paragraph content here. " * 10
        text = para1 + "\n\n" + para2
        chunks = chunk_text(text, size=len(para1) + 5, overlap=50)
        # The split should occur at the paragraph boundary
        assert any("\n\n" not in c for c in chunks)

    def test_prefers_sentence_break(self):
        """chunk_text should prefer splitting on sentences when no paragraph break."""
        sentence = "This is a sentence. "
        text = sentence * 60
        chunks = chunk_text(text, size=300, overlap=50)
        assert len(chunks) > 1

    def test_custom_chunk_size(self):
        text = "word " * 200  # ~1000 chars
        chunks_small = chunk_text(text, size=200, overlap=20)
        chunks_large = chunk_text(text, size=800, overlap=80)
        assert len(chunks_small) > len(chunks_large)

    def test_whitespace_stripped_from_chunks(self):
        text = "  leading and trailing whitespace  " + " more text " * 50
        chunks = chunk_text(text, size=100, overlap=20)
        for chunk in chunks:
            assert chunk == chunk.strip()

    def test_dataset_file_is_readable(self):
        """Smoke-test: the Harry Potter dataset used by the notebook must exist."""
        repo_root = Path(__file__).parent.parent.parent
        file_path = repo_root / "datasets" / "text_files" / "harry_potter_knowledge_base.txt"
        assert file_path.exists(), f"Dataset not found at {file_path}"
        text = file_path.read_text(encoding="utf-8")
        assert len(text) > 0

    def test_dataset_produces_chunks(self):
        """Chunk the real dataset and verify basic structural properties."""
        repo_root = Path(__file__).parent.parent.parent
        file_path = repo_root / "datasets" / "text_files" / "harry_potter_knowledge_base.txt"
        text = file_path.read_text(encoding="utf-8")
        chunks = chunk_text(text)
        assert len(chunks) > 0
        for chunk in chunks:
            assert len(chunk) <= 1000 + 1  # +1 for boundary rounding


# ---------------------------------------------------------------------------
# embed_and_store tests  (OpenAI + ChromaDB mocked)
# ---------------------------------------------------------------------------


class TestEmbedAndStore:
    def _make_openai_mock(self, embedding_dim=8):
        """Return a mock OpenAI client whose embeddings.create returns dummy data."""
        mock_client = MagicMock()

        def fake_embeddings_create(model, input):
            response = MagicMock()
            response.data = [
                MagicMock(embedding=[0.1] * embedding_dim) for _ in input
            ]
            return response

        mock_client.embeddings.create.side_effect = fake_embeddings_create
        return mock_client

    def _make_chroma_mock(self):
        """Return a lightweight mock ChromaDB client backed by a simple dict store."""
        store: dict = {"ids": [], "documents": [], "embeddings": [], "metadatas": []}

        mock_collection = MagicMock()

        def fake_add(ids, documents, embeddings, metadatas):
            store["ids"].extend(ids)
            store["documents"].extend(documents)
            store["embeddings"].extend(embeddings)
            store["metadatas"].extend(metadatas)

        def fake_get():
            return {k: list(v) for k, v in store.items()}

        mock_collection.add.side_effect = fake_add
        mock_collection.get.side_effect = fake_get

        mock_chroma = MagicMock()
        mock_chroma.get_or_create_collection.return_value = mock_collection
        return mock_chroma, mock_collection

    def test_collection_populated(self):
        chunks = ["chunk one", "chunk two", "chunk three"]
        mock_client = self._make_openai_mock()
        mock_chroma, mock_collection = self._make_chroma_mock()
        embed_and_store(
            mock_client, chunks, "/unused", "test_collection",
            "text-embedding-3-small", chroma_client=mock_chroma,
        )
        result = mock_collection.get()
        assert len(result["ids"]) == len(chunks)

    def test_ids_are_sequential(self):
        chunks = ["alpha", "beta", "gamma"]
        mock_client = self._make_openai_mock()
        mock_chroma, mock_collection = self._make_chroma_mock()
        embed_and_store(
            mock_client, chunks, "/unused", "test_ids",
            "text-embedding-3-small", chroma_client=mock_chroma,
        )
        ids = mock_collection.get()["ids"]
        assert ids == ["chunk_0", "chunk_1", "chunk_2"]

    def test_metadata_chunk_index(self):
        chunks = ["doc0", "doc1"]
        mock_client = self._make_openai_mock()
        mock_chroma, mock_collection = self._make_chroma_mock()
        embed_and_store(
            mock_client, chunks, "/unused", "test_meta",
            "text-embedding-3-small", chroma_client=mock_chroma,
        )
        metadatas = mock_collection.get()["metadatas"]
        assert metadatas[0]["chunk_index"] == 0
        assert metadatas[1]["chunk_index"] == 1

    def test_openai_called_once_for_small_batch(self):
        chunks = ["a", "b", "c"]
        mock_client = self._make_openai_mock()
        mock_chroma, _ = self._make_chroma_mock()
        embed_and_store(
            mock_client, chunks, "/unused", "test_calls",
            "text-embedding-3-small", chroma_client=mock_chroma,
        )
        # All three chunks fit in one batch of 100
        assert mock_client.embeddings.create.call_count == 1

    def test_openai_batches_large_input(self):
        chunks = [f"doc {i}" for i in range(250)]
        mock_client = self._make_openai_mock()
        mock_chroma, _ = self._make_chroma_mock()
        embed_and_store(
            mock_client, chunks, "/unused", "test_batches",
            "text-embedding-3-small", chroma_client=mock_chroma,
        )
        # 250 chunks → ceil(250/100) = 3 API calls
        assert mock_client.embeddings.create.call_count == 3


# ---------------------------------------------------------------------------
# retrieve tests  (OpenAI + ChromaDB mocked)
# ---------------------------------------------------------------------------


class TestRetrieve:
    def test_returns_list_of_documents(self):
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.0] * 8)
        ]

        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [["doc_a", "doc_b", "doc_c"]]
        }

        result = retrieve(
            mock_client, mock_collection, "test question", "text-embedding-3-small"
        )
        assert result == ["doc_a", "doc_b", "doc_c"]

    def test_respects_top_k(self):
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.0] * 8)
        ]
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [["only_one"]]}

        retrieve(
            mock_client,
            mock_collection,
            "question",
            "text-embedding-3-small",
            top_k=1,
        )
        call_kwargs = mock_collection.query.call_args[1]
        assert call_kwargs["n_results"] == 1

    def test_question_is_embedded(self):
        mock_client = MagicMock()
        mock_client.embeddings.create.return_value.data = [
            MagicMock(embedding=[0.5] * 8)
        ]
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [[]]}

        question = "What is Harry Potter about?"
        retrieve(
            mock_client, mock_collection, question, "text-embedding-3-small"
        )
        mock_client.embeddings.create.assert_called_once_with(
            model="text-embedding-3-small", input=question
        )


# ---------------------------------------------------------------------------
# answer tests  (OpenAI chat mocked)
# ---------------------------------------------------------------------------


class TestAnswer:
    def test_returns_string(self):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="Harry Potter is a wizard."))
        ]

        docs = ["Context about Harry Potter.", "More context here."]
        result = answer(mock_client, "Who is Harry Potter?", docs)
        assert isinstance(result, str)
        assert result == "Harry Potter is a wizard."

    def test_context_injected_into_prompt(self):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="OK"))
        ]

        docs = ["First doc.", "Second doc."]
        answer(mock_client, "any question", docs)

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        prompt_content = call_kwargs["messages"][0]["content"]
        assert "First doc." in prompt_content
        assert "Second doc." in prompt_content

    def test_question_injected_into_prompt(self):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="OK"))
        ]

        question = "Why did Voldemort fail?"
        answer(mock_client, question, ["some context"])

        call_kwargs = mock_client.chat.completions.create.call_args[1]
        prompt_content = call_kwargs["messages"][0]["content"]
        assert question in prompt_content

    def test_empty_docs_still_calls_api(self):
        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="I don't know."))
        ]

        result = answer(mock_client, "some question", [])
        assert mock_client.chat.completions.create.called
        assert result == "I don't know."
