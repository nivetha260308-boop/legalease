import html
import re
import unicodedata


def sanitize_text(text: str) -> str:
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text)

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "-",
        "\u00a0": " ",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\x00", "", text)

    return text.strip()


def safe_html(text: str) -> str:
    return html.escape(sanitize_text(text))


def parse_terms(terms: str) -> list[str]:
    cleaned = sanitize_text(terms)

    if not cleaned:
        return []

    return [
        part.strip()
        for part in cleaned.split(";")
        if part.strip()
    ]


def split_document(text: str) -> list[str]:
    cleaned = sanitize_text(text)

    return [
        paragraph.strip()
        for paragraph in re.split(
            r"\n\s*\n+",
            cleaned
        )
        if paragraph.strip()
    ]


def looks_like_heading(line: str) -> bool:

    value = line.strip()

    if not value or len(value) > 100:
        return False

    return bool(
        value.isupper()
        or re.match(
            r"^(ARTICLE|SECTION|CLAUSE|EXHIBIT|SCHEDULE)\b",
            value,
            re.IGNORECASE
        )
        or re.match(
            r"^\d+[.)]\s+",
            value
        )
    )