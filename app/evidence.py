from __future__ import annotations

import math
import re
from collections import Counter


TOKEN_RE = re.compile(r"[a-zA-ZÀ-ÿ0-9][a-zA-ZÀ-ÿ0-9_-]{1,}")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "da", "das", "de", "do",
    "dos", "e", "em", "for", "from", "in", "is", "it", "of", "on", "or", "para",
    "the", "to", "um", "uma", "with",
}


def tokens(value: str) -> list[str]:
    return [
        token.lower()
        for token in TOKEN_RE.findall(value)
        if token.lower() not in STOPWORDS
    ]


def lexical_score(query: str, content: str) -> float:
    query_tokens = tokens(query)
    content_tokens = tokens(content)
    if not query_tokens or not content_tokens:
        return 0.0

    q = Counter(query_tokens)
    c = Counter(content_tokens)
    overlap = sum(min(q[token], c[token]) for token in q)
    coverage = overlap / max(1, sum(q.values()))

    lowered_query = " ".join(query.lower().split())
    lowered_content = " ".join(content.lower().split())
    phrase_bonus = 0.25 if len(lowered_query) >= 5 and lowered_query in lowered_content else 0.0

    rarity_bonus = sum(1 / math.sqrt(max(c[token], 1)) for token in q if token in c)
    rarity_bonus = min(0.2, rarity_bonus / max(1, len(q)) * 0.08)

    return round(min(1.0, coverage + phrase_bonus + rarity_bonus), 4)
