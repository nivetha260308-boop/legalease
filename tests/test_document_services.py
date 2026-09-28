from backend.services.document_service import (
    format_docx,
    format_pdf,
    format_txt,
)

from backend.utils.text_utils import (
    parse_terms,
    sanitize_text,
)


def test_sanitize_text():

    assert (
        sanitize_text(
            "“Hello”—world"
        )
        == '"Hello"-world'
    )


def test_parse_terms():

    assert (
        parse_terms(
            "One; Two ; Three"
        )
        == [
            "One",
            "Two",
            "Three",
        ]
    )


def test_exports_are_nonempty():

    text = (
        "GENERAL AGREEMENT\n\n"
        "1. PARTIES\n"
        "Jane Doe and ABC Ltd."
    )

    assert (
        format_txt(text)
        .startswith(b"GENERAL")
    )

    assert (
        format_docx(
            text,
            "General Agreement"
        )
        .startswith(b"PK")
    )

    assert (
        format_pdf(
            text,
            "General Agreement"
        )
        .startswith(b"%PDF")
    )