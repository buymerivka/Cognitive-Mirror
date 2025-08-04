import re
from dataclasses import dataclass
from typing import List

import spacy

nlp = spacy.load('en_core_web_sm')


@dataclass
class ParsedSentence:
    paragraphIndex: int
    sentenceIndex: int
    text: str
    charStart: int
    charEnd: int


def replace_html_tags_with_spaces(text: str) -> str:
    def replacer(match: re.Match) -> str:
        return ' ' * len(match.group(0))

    return re.sub(r'<[^>]+>', replacer, text)


def preprocessing(text: str) -> List[ParsedSentence]:
    cleaned = text.replace('\r\n', '\n').replace('\r', '\n')
    cleaned = re.sub(r'\n\s*\n+', '\n\n', cleaned)
    cleaned = cleaned.strip()
    cleaned = replace_html_tags_with_spaces(cleaned)
    paragraphs = cleaned.split('\n\n')
    offset = 0
    result = []

    for p_idx, paragraph in enumerate(paragraphs):
        doc = nlp(paragraph)
        for s_idx, sent in enumerate(doc.sents):
            abs_start = text.find(sent.text.split()[0], offset)
            item = sent.text
            item = item.strip()
            abs_end = abs_start + len(item)
            item = re.sub(r'[ \t]+', ' ', item)
            result.append(
                ParsedSentence(
                    paragraphIndex=p_idx,
                    sentenceIndex=s_idx,
                    text=item,
                    charStart=abs_start,
                    charEnd=abs_end - 1
                )
            )
            offset = abs_end

    return result


def clean_text(text):
    # Remove newline characters and extra spaces
    text = re.sub(r'\s+', ' ', text)

    # Remove unwanted punctuation (keep apostrophes and hyphens for GloVe compatibility)
    text = re.sub(r'[^\w\s\'-]', '', text)

    # Lowercase
    text = text.lower()

    # Optionally: remove standalone digits (not words like "brl 300")
    text = re.sub(r'\b\d+\b', '', text)

    # Strip leading/trailing whitespace
    return text.strip()