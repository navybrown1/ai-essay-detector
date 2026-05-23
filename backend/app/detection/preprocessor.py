import re
import os
from typing import Tuple


def clean_text(text: str) -> str:
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


_NLTK_DATA_DIR = "/tmp/nltk_data"
_BUNDLED_NLTK_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "nltk_data")


def _ensure_nltk_data():
    """Ensure required NLTK tokenizers are available."""
    import nltk
    os.makedirs(_NLTK_DATA_DIR, exist_ok=True)
    nltk.data.path.insert(0, _NLTK_DATA_DIR)
    if os.path.isdir(_BUNDLED_NLTK_DIR):
        nltk.data.path.insert(0, _BUNDLED_NLTK_DIR)

    for resource in ("tokenizers/punkt_tab", "tokenizers/punkt"):
        try:
            nltk.data.find(resource, paths=nltk.data.path)
        except LookupError:
            nltk.download(resource.split("/")[-1], quiet=True, download_dir=_NLTK_DATA_DIR)


def segment_sentences(text: str) -> list[str]:
    _ensure_nltk_data()
    import nltk
    return nltk.sent_tokenize(text)


def segment_paragraphs(text: str) -> list[str]:
    raw = re.split(r"\n\s*\n", text)
    return [p.strip() for p in raw if p.strip()]


def tokenize_words(text: str) -> list[str]:
    return re.findall(r"\b[a-zA-Z]+\b", text.lower())


def extract_ngrams(tokens: list[str], n: int) -> set:
    return set(zip(*[tokens[i:] for i in range(n)]))


def count_syllables(word: str) -> int:
    word = word.lower()
    count = 0
    vowels = "aeiouy"
    if word and word[0] in vowels:
        count += 1
    for i in range(1, len(word)):
        if word[i] in vowels and word[i - 1] not in vowels:
            count += 1
    if word.endswith("e"):
        count -= 1
    if word.endswith("le") and len(word) > 2 and word[-3] not in vowels:
        count += 1
    return max(1, count)
