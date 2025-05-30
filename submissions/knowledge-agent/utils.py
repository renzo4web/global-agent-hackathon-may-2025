import tiktoken
import PyPDF2
import io
import streamlit as st


def count_tokens(text):
    """Count tokens using tiktoken, fallback to simple estimation"""
    try:
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except:
        return len(text) // 4


def process_pdf(uploaded_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
        text_parts = []
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text.strip():
                text_parts.append(text)

        return "\n\n".join(text_parts)
    except Exception as e:
        raise Exception(f"Error reading PDF: {str(e)}")


def format_source_title(content, prefix="📝", max_length=60):
    """Format source title with emoji prefix and length limit"""
    return f"{prefix} {content[:max_length]}..."


def create_download_button(label, data, file_name_prefix, key_suffix,
                           use_container_width=False, is_primary=False):
    """Create a download button with consistent styling"""
    st.download_button(
        label=label,
        data=data,
        file_name=f"{file_name_prefix.lower().replace(' ', '_')}_{key_suffix}.md",
        mime="text/markdown",
        key=f"download_{key_suffix.replace(' ', '_')}_{file_name_prefix.replace(' ', '_')}",
        use_container_width=use_container_width,
        type="primary" if is_primary else "secondary"
    )


def combine_sources(sources):
    """Combine all source contents with separators"""
    return "\n\n--- Source Separator ---\n\n".join(
        [f"Source {i + 1}:\n{s['content']}" for i, s in enumerate(sources)]
    )

