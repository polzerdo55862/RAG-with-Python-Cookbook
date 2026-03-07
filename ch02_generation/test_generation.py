"""
Tests for the ch02_generation/generation.ipynb notebook code.
"""

from datetime import date
from typing import List
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel, ValidationError


# ---------------------------------------------------------------------------
# Pydantic models (copied from the notebook, Section 6)
# ---------------------------------------------------------------------------

class LineItem(BaseModel):
    description: str
    quantity: int
    total: float


class Invoice(BaseModel):
    invoice_number: str
    invoice_date: date
    supplier: str
    items: List[LineItem]
    total_due: float


# ---------------------------------------------------------------------------
# ask_with_context helper (copied from the notebook, Section 1)
# ---------------------------------------------------------------------------

def ask_with_context(context: str, question: str, client=None) -> str:
    """Ask a question given a context using the OpenAI chat API."""
    from openai import OpenAI

    if client is None:
        client = OpenAI()

    messages = [
        {
            "role": "system",
            "content": "Answer based only on the provided context.",
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion:\n{question}",
        },
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Tests – LineItem model
# ---------------------------------------------------------------------------

class TestLineItem:
    def test_valid_line_item(self):
        item = LineItem(description="Laptop", quantity=2, total=2000.0)
        assert item.description == "Laptop"
        assert item.quantity == 2
        assert item.total == 2000.0

    def test_quantity_is_integer(self):
        item = LineItem(description="Mouse", quantity=5, total=100.0)
        assert isinstance(item.quantity, int)

    def test_total_is_float(self):
        item = LineItem(description="Keyboard", quantity=1, total=49.99)
        assert isinstance(item.total, float)

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            LineItem(description="Widget", quantity=1)  # missing total


# ---------------------------------------------------------------------------
# Tests – Invoice model
# ---------------------------------------------------------------------------

class TestInvoice:
    def _make_invoice(self, **overrides):
        defaults = dict(
            invoice_number="INV-001",
            invoice_date=date(2024, 1, 15),
            supplier="Tech Corp",
            items=[
                LineItem(description="Laptop", quantity=2, total=2000.0),
                LineItem(description="Mouse", quantity=5, total=100.0),
            ],
            total_due=2100.0,
        )
        defaults.update(overrides)
        return Invoice(**defaults)

    def test_valid_invoice(self):
        inv = self._make_invoice()
        assert inv.invoice_number == "INV-001"
        assert inv.supplier == "Tech Corp"
        assert inv.total_due == 2100.0

    def test_invoice_date_parsed_from_string(self):
        inv = Invoice(
            invoice_number="INV-002",
            invoice_date="2024-06-01",
            supplier="Acme",
            items=[LineItem(description="Widget", quantity=1, total=10.0)],
            total_due=10.0,
        )
        assert inv.invoice_date == date(2024, 6, 1)

    def test_invoice_contains_line_items(self):
        inv = self._make_invoice()
        assert len(inv.items) == 2
        descriptions = [item.description for item in inv.items]
        assert "Laptop" in descriptions
        assert "Mouse" in descriptions

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            Invoice(
                invoice_number="INV-003",
                invoice_date=date(2024, 1, 1),
                supplier="Corp",
                # items missing
                total_due=0.0,
            )

    def test_empty_items_list(self):
        inv = self._make_invoice(items=[])
        assert inv.items == []


# ---------------------------------------------------------------------------
# Tests – ask_with_context
# ---------------------------------------------------------------------------

class TestAskWithContext:
    def _make_mock_client(self, answer: str) -> MagicMock:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = answer
        mock_client.chat.completions.create.return_value = mock_response
        return mock_client

    def test_returns_string(self):
        mock_client = self._make_mock_client("RAG stands for Retrieval-Augmented Generation.")
        result = ask_with_context("RAG stands for Retrieval-Augmented Generation.", "What does RAG stand for?", client=mock_client)
        assert isinstance(result, str)

    def test_correct_answer_returned(self):
        expected = "RAG stands for Retrieval-Augmented Generation."
        mock_client = self._make_mock_client(expected)
        result = ask_with_context("RAG stands for Retrieval-Augmented Generation.", "What does RAG stand for?", client=mock_client)
        assert result == expected

    def test_messages_contain_context_and_question(self):
        mock_client = self._make_mock_client("Paris")
        context = "France is a country in Europe. Its capital is Paris."
        question = "What is the capital of France?"
        ask_with_context(context, question, client=mock_client)

        call_args = mock_client.chat.completions.create.call_args
        if "messages" in call_args.kwargs:
            messages = call_args.kwargs["messages"]
        else:
            messages = call_args.args[0]
        # Collect all message content as a single string for easy assertion
        all_content = " ".join(m["content"] for m in messages)
        assert context in all_content
        assert question in all_content

    def test_system_message_present(self):
        mock_client = self._make_mock_client("42")
        ask_with_context("Some context.", "Some question?", client=mock_client)

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        messages = call_kwargs["messages"]
        roles = [m["role"] for m in messages]
        assert "system" in roles

    def test_model_is_gpt4o_mini(self):
        mock_client = self._make_mock_client("ok")
        ask_with_context("ctx", "q?", client=mock_client)

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "gpt-4o-mini"
