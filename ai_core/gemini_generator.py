from __future__ import annotations

from google import genai
from google.genai import types

from backend.utils.config import Settings
from backend.utils.text_utils import (
    parse_terms,
    sanitize_text,
)


class GeminiDocumentGenerator:

    def __init__(self, settings: Settings):

        self.settings = settings

        if settings.gemini_api_key:
            self.client = genai.Client(
                api_key=settings.gemini_api_key
            )
        else:
            self.client = None

    def _build_prompt(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str,
    ) -> str:

        term_lines = "\n".join(
            f"- {term}"
            for term in parse_terms(terms)
        )

        if not term_lines:
            term_lines = "- No additional terms supplied."

        prompt = f"""
You are LegalEase, an AI drafting assistant.

Create a professional LEGAL DOCUMENT DRAFT using ONLY
the information supplied by the user.

IMPORTANT RULES:

1. This is an AI-generated draft for informational purposes.
2. It is NOT legal advice.
3. Never invent names, dates, addresses, money amounts,
   obligations, or legal facts.
4. Preserve supplied party names accurately.
5. Preserve supplied terms accurately.
6. If an important fact is missing, write:
   [TO BE COMPLETED]
7. Use professional and neutral legal language.
8. Use a clear document title.
9. Use numbered sections.
10. Include signature blocks where appropriate.
11. Include the effective date.
12. Include jurisdiction when supplied.
13. Do not claim guaranteed legal validity.
14. Do not say that the document is legally valid.
15. End with a short Drafting Notice.
16. Do not use Markdown code fences.
17. Return ONLY the document.

DOCUMENT TYPE:
{sanitize_text(document_type)}

PARTIES:
{sanitize_text(parties)}

EFFECTIVE DATE:
{sanitize_text(effective_date) or "[TO BE COMPLETED]"}

JURISDICTION:
{sanitize_text(jurisdiction) or "[TO BE COMPLETED]"}

USER-SUPPLIED TERMS:
{term_lines}
"""

        return prompt.strip()

    def _demo_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str,
    ) -> str:

        terms_list = parse_terms(terms)

        lines = [
            sanitize_text(document_type).upper()
            or "LEGAL DOCUMENT DRAFT",

            "",

            "DRAFTING NOTICE",

            (
                "This sample was generated in local demo mode. "
                "It is not legal advice and must be reviewed by "
                "a qualified legal professional before use."
            ),

            "",

            "1. PARTIES",

            sanitize_text(parties)
            or "[PARTIES TO BE COMPLETED]",

            "",

            "2. EFFECTIVE DATE",

            sanitize_text(effective_date)
            or "[TO BE COMPLETED]",

            "",

            "3. JURISDICTION",

            sanitize_text(jurisdiction)
            or "[TO BE COMPLETED]",

            "",

            "4. TERMS AND CONDITIONS",
        ]

        if terms_list:
            for index, term in enumerate(
                terms_list,
                start=1
            ):
                lines.append(
                    f"{index}. {term}"
                )
        else:
            lines.append(
                "[TERMS TO BE COMPLETED]"
            )

        lines.extend(
            [
                "",
                "5. GENERAL",
                (
                    "The parties should obtain appropriate "
                    "legal review before signing or relying "
                    "on this draft."
                ),
                "",
                "SIGNATURES",
                (
                    "Party 1: ______________________________    "
                    "Date: ______________"
                ),
                (
                    "Party 2: ______________________________    "
                    "Date: ______________"
                ),
            ]
        )

        return "\n".join(lines)

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        effective_date: str,
        jurisdiction: str,
    ) -> str:

        if self.settings.demo_mode or not self.client:
            return self._demo_document(
                document_type,
                parties,
                terms,
                effective_date,
                jurisdiction,
            )

        response = self.client.models.generate_content(
            model=self.settings.gemini_model,

            contents=self._build_prompt(
                document_type,
                parties,
                terms,
                effective_date,
                jurisdiction,
            ),

            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=12000,
                candidate_count=1,
            ),
        )

        generated_text = getattr(
            response,
            "text",
            None
        )

        if not generated_text:
            raise RuntimeError(
                "Gemini returned no text. "
                "Check the API key, model, or safety response."
            )

        return sanitize_text(generated_text)