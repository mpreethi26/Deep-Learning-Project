"""
Central Configuration for Abstractive Text Summarization Application.
"""
from typing import Dict, Any

# Project Metadata
PROJECT_TITLE = "Abstractive Text Summarization Using Transformer Models"
TEAM_LEAD = "CHOUDAM BHARATH REDDY"
APPLICATION_AREA = "Text Summarization"
NLP_DOMAIN = "Natural Language Processing (NLP)"
RESEARCH_KEYWORDS = "abstractive text summarization transformer"
REQUIRED_PUBLISHER = "IEEE Xplore"

# Supported Models Configuration - Exactly Two Transformer Models
DEFAULT_MODEL_KEY = "t5_small"

SUPPORTED_MODELS: Dict[str, Dict[str, Any]] = {
    "t5_small": {
        "display_name": "T5-small (Falconsai/text_summarization)",
        "model_id": "Falconsai/text_summarization",
        "architecture": "T5-small (Text-to-Text Transfer Transformer)",
        "framework": "Encoder-Decoder (Seq2Seq)",
        "max_input_tokens": 512,
        "is_encoder_decoder": True,
        "default_prefix": "",
        "notes": "Default model. Fine-tuned specifically for abstractive text summarization. Ultra-fast 60M parameter architecture."
    },
    "distilbart": {
        "display_name": "DistilBART (sshleifer/distilbart-cnn-12-6)",
        "model_id": "sshleifer/distilbart-cnn-12-6",
        "architecture": "DistilBART (Bidirectional and Auto-Regressive Transformers)",
        "framework": "Encoder-Decoder (Seq2Seq)",
        "max_input_tokens": 1024,
        "is_encoder_decoder": True,
        "default_prefix": "",
        "notes": "Optional comparative model. Distilled from BART-Large-CNN with high discourse coherence."
    }
}

# Backward compatibility alias map
MODEL_ALIASES = {
    "bart": "distilbart",
    "t5": "t5_small",
}

# Summary Length Profiles
# Word count targets:
# - Short: 60–100 words
# - Medium: 120–180 words
# - Long: 200–350 words
# - Detailed: 350–500 words
LENGTH_PROFILES: Dict[str, Dict[str, Any]] = {
    "short": {
        "label": "Short (Key Takeaways)",
        "description": "Essential facts, core findings, and high-level takeaway.",
        "target_word_min": 60,
        "target_word_max": 100,
        "min_tokens": 50,
        "max_tokens": 120,
        "num_beams": 2,
        "length_penalty": 1.2,
        "no_repeat_ngram_size": 3,
        "chunk_intermediate_tokens": 60,
    },
    "medium": {
        "label": "Medium (Balanced Summary)",
        "description": "Main ideas, supporting context, and key outcomes.",
        "target_word_min": 120,
        "target_word_max": 180,
        "min_tokens": 90,
        "max_tokens": 200,
        "num_beams": 2,
        "length_penalty": 1.5,
        "no_repeat_ngram_size": 3,
        "chunk_intermediate_tokens": 100,
    },
    "long": {
        "label": "Long (Comprehensive Coverage)",
        "description": "Thorough coverage of all major topics, arguments, methodology, and conclusions.",
        "target_word_min": 200,
        "target_word_max": 350,
        "min_tokens": 180,
        "max_tokens": 360,
        "num_beams": 2,
        "length_penalty": 1.8,
        "no_repeat_ngram_size": 3,
        "chunk_intermediate_tokens": 140,
    },
    "detailed": {
        "label": "Detailed (Exhaustive Synthesis)",
        "description": "Deep analytical synthesis preserving key nuances, findings, evidence, and limitations.",
        "target_word_min": 350,
        "target_word_max": 500,
        "min_tokens": 280,
        "max_tokens": 480,
        "num_beams": 2,
        "length_penalty": 2.0,
        "no_repeat_ngram_size": 3,
        "chunk_intermediate_tokens": 180,
    }
}

# Long Document Chunking Settings
CHUNK_SETTINGS = {
    "max_chunk_tokens": 450,  # Conservatively fits T5-small (512) and DistilBART (1024)
    "overlap_tokens": 30,     # Reduced overlap avoids redundant re-processing
    "max_chunks_limit": 5,    # Caps intermediate segments to avoid CPU timeout
    "chunk_safety_margin": 40,
}

# PDF Processing Settings
PDF_SETTINGS = {
    "max_file_size_mb": 25.0,
    "max_preview_chars": 5000,
}

# UI Theme / Palette
UI_THEME = {
    "primary": "#1E3A8A",      # Deep navy
    "accent": "#4F46E5",       # Indigo
    "bg_subtle": "#F8FAFC",    # Soft neutral
    "border": "#E2E8F0",
    "text_dark": "#0F172A",
}
