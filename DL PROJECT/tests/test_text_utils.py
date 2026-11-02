"""
Unit Tests for Text Utilities.
"""
import pytest
from utils.text_utils import (
    clean_text,
    validate_input_text,
    compute_text_stats,
    calculate_compression_ratio,
    chunk_text_by_tokens
)

class DummyTokenizer:
    """Mock tokenizer for unit testing chunking logic without heavy model loads."""
    def encode(self, text, add_special_tokens=False):
        return [1] * len(text.split())

    def decode(self, token_ids, skip_special_tokens=True):
        return f"decoded_{len(token_ids)}_words"

def test_clean_text():
    dirty = "  Hello   world!\r\n\r\n\r\nThis is\xa0a test.  "
    cleaned = clean_text(dirty)
    assert "Hello world!" in cleaned
    assert "This is a test." in cleaned
    assert "\r" not in cleaned
    assert "\xa0" not in cleaned

def test_validate_input_text_empty():
    valid, msg = validate_input_text("")
    assert not valid
    assert "empty" in msg.lower()

    valid, msg = validate_input_text("   \n\t  ")
    assert not valid

def test_validate_input_text_too_short():
    valid, msg = validate_input_text("Only three words")
    assert not valid
    assert "too short" in msg.lower()

def test_validate_input_text_valid():
    valid, msg = validate_input_text("This is a sufficiently long sentence for our validation.")
    assert valid
    assert msg == ""

def test_compute_text_stats():
    text = "First sentence here. Second sentence follows. Third sentence ends!"
    stats = compute_text_stats(text)
    assert stats["word_count"] == 9
    assert stats["sentence_count"] == 3
    assert stats["char_count"] > 0

def test_calculate_compression_ratio():
    ratio = calculate_compression_ratio(original_words=100, summary_words=25)
    assert ratio == 75.0

    # Summary larger or equal to original
    ratio_equal = calculate_compression_ratio(original_words=50, summary_words=60)
    assert ratio_equal == 0.0

def test_chunk_text_by_tokens():
    tokenizer = DummyTokenizer()
    long_text = "Sentence one. " * 50
    chunks = chunk_text_by_tokens(long_text, tokenizer, max_chunk_tokens=30, overlap_tokens=5)
    assert len(chunks) > 1
    assert all(len(c) > 0 for c in chunks)
