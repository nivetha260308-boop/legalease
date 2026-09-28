from datetime import date

import requests
import streamlit as st

from backend.services.document_service import (
    format_docx,
    format_pdf,
    format_txt,
)

from backend.utils.config import (
    get_settings,
)

from backend.utils.text_utils import (
    safe_html,
)


settings = get_settings()


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


st.markdown(
    """
<style>

.main-title {
    text-align: center;
    margin-bottom: 0;
}

.subtitle {
    text-align: center;
    color: #8b93a7;
}

.preview {
    background: #111827;
    color: #f3f4f6;
    border-radius: 14px;
    padding: 24px;
    min-height: 360px;
    max-height: 620px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-family: Georgia, serif;
    line-height: 1.65;
    border: 1px solid #273244;
}

.notice {
    background: #fff8e7;
    border-left: 4px solid #e3a008;
    padding: 12px 16px;
    border-radius: 8px;
    color: #4b3b12;
}

</style>
""",
    unsafe_allow_html=True,
)


st.markdown(
    '<h1 class="main-title">⚖️ LegalEase</h1>',
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="subtitle">'
    'AI-powered legal document drafting workspace'
    '</p>',
    unsafe_allow_html=True,
)


st.markdown(
    """
<div class="notice">

<b>Important:</b>

LegalEase creates drafts for informational
purposes. It is not legal advice.

Review generated documents with a qualified
legal professional before signing or relying
on them.

</div>
""",
    unsafe_allow_html=True,
)


if "document" not in st.session_state:
    st.session_state.document = ""


if "last_meta" not in st.session_state:
    st.session_state.last_meta = {}


with st.sidebar:

    st.header(
        "📄 Document details"
    )

    document_type = st.selectbox(
        "Document type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement",
            "Lease Agreement",
            "Freelance Work Contract",
            "Service Agreement",
            "Employment Offer Letter",
            "General Agreement",
            "Custom",
        ],
    )

    if document_type == "Custom":

        document_type = st.text_input(
            "Custom document type",
            placeholder=(
                "e.g. Consulting Agreement"
            ),
        )

    parties = st.text_area(
        "Parties involved",
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=100,
    )

    effective_date = st.date_input(
        "Effective date",
        value=date.today(),
    )

    jurisdiction = st.text_input(
        "Jurisdiction (optional)",
        placeholder=(
            "e.g. Tamil Nadu, India"
        ),
    )

    terms = st.text_area(
        "Terms & conditions",
        placeholder=(
            "Payment within 30 days of invoice; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=180,
    )

    generate = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True,
    )


if generate:

    if (
        not document_type.strip()
        or not parties.strip()
    ):

        st.error(
            "Please enter both the "
            "document type and parties involved."
        )

    else:

        payload = {
            "document_type": (
                document_type.strip()
            ),
            "parties": parties.strip(),
            "terms": terms.strip(),
            "effective_date": (
                effective_date.isoformat()
            ),
            "jurisdiction": (
                jurisdiction.strip()
            ),
        }

        with st.spinner(
            "🤖 Drafting your document..."
        ):

            try:

                response = requests.post(
                    (
                        f"{settings.frontend_api_url.rstrip('/')}"
                        "/generate"
                    ),
                    json=payload,
                    timeout=120,
                )

                response.raise_for_status()

                data = response.json()

                st.session_state.document = (
                    data["document"]
                )

                st.session_state.last_meta = data

                st.success(
                    "Document generated successfully."
                )

            except requests.RequestException as exc:

                st.error(
                    "Could not reach the FastAPI backend."
                )

                st.info(
                    "Start the backend using:"
                )

                st.code(
                    "uvicorn backend.main:app --reload"
                )

                st.caption(
                    str(exc)
                )


left, right = st.columns(
    [1.15, 1]
)


with left:

    st.subheader(
        "📑 Generated document"
    )

    if st.session_state.document:

        st.markdown(
            (
                '<div class="preview">'
                f'{safe_html(st.session_state.document)}'
                '</div>'
            ),
            unsafe_allow_html=True,
        )

    else:

        st.info(
            "Your generated document will appear here."
        )


with right:

    st.subheader(
        "✏️ Editable version"
    )

    edited = st.text_area(
        "Edit document",
        value=st.session_state.document,
        height=510,
        label_visibility="collapsed",
    )

    if st.session_state.document:

        st.session_state.document = edited

        st.markdown(
            "#### 📥 Download"
        )

        txt_bytes = format_txt(
            edited
        )

        docx_bytes = format_docx(
            edited,
            document_type,
            terms=terms,
        )

        pdf_bytes = format_pdf(
            edited,
            document_type,
            terms=terms,
        )

        c1, c2, c3 = st.columns(3)

        with c1:

            st.download_button(
                "⬇️ TXT",
                txt_bytes,
                "legalease_document.txt",
                "text/plain",
                use_container_width=True,
            )

        with c2:

            st.download_button(
                "⬇️ DOCX",
                docx_bytes,
                "legalease_document.docx",
                (
                    "application/"
                    "vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True,
            )

        with c3:

            st.download_button(
                "⬇️ PDF",
                pdf_bytes,
                "legalease_document.pdf",
                "application/pdf",
                use_container_width=True,
            )

        metadata = (
            st.session_state.last_meta
        )

        if metadata:

            st.caption(
                "Generation source: "
                f"{metadata.get('model', 'unknown')} "
                "• Demo mode: "
                f"{metadata.get('demo_mode', False)}"
            )


st.divider()


st.caption(
    "LegalEase • Drafting assistant only • "
    "Do not treat generated content as legal advice."
)