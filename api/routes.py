from fastapi import (
    APIRouter,
    HTTPException,
)

from pydantic import (
    BaseModel,
    Field,
)

from backend.ai_core.gemini_generator import (
    GeminiDocumentGenerator,
)

from backend.utils.config import (
    get_settings,
)


router = APIRouter(
    tags=["documents"]
)


class DocumentRequest(BaseModel):

    document_type: str = Field(
        ...,
        min_length=2,
        max_length=200,
    )

    parties: str = Field(
        ...,
        min_length=2,
        max_length=5000,
    )

    terms: str = Field(
        default="",
        max_length=10000,
    )

    effective_date: str = Field(
        default="",
        max_length=100,
    )

    jurisdiction: str = Field(
        default="",
        max_length=200,
    )


class DocumentResponse(BaseModel):

    document: str

    model: str

    demo_mode: bool


@router.post(
    "/generate",
    response_model=DocumentResponse,
)
def generate_document(
    payload: DocumentRequest,
):

    settings = get_settings()

    try:

        generator = GeminiDocumentGenerator(
            settings
        )

        document = generator.generate_document(
            payload.document_type,
            payload.parties,
            payload.terms,
            payload.effective_date,
            payload.jurisdiction,
        )

        document = document[
            :settings.max_document_chars
        ]

        demo_mode = (
            settings.demo_mode
            or not bool(settings.gemini_api_key)
        )

        return DocumentResponse(
            document=document,
            model=(
                "demo"
                if demo_mode
                else settings.gemini_model
            ),
            demo_mode=demo_mode,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=502,
            detail=(
                "Document generation failed: "
                f"{exc}"
            ),
        ) from exc