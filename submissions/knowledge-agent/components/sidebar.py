import streamlit as st
from agents import DEFAULT_MODEL_ID, DEFAULT_BASE_URL


def render_sidebar():
    """Render the sidebar with configuration options"""
    with st.sidebar:
        st.markdown("## Configuration")

        api_key = st.text_input(
            "🔑 OpenAI API Key",
            type="password",
            help="Your API key is required to power the AI analyses.\n We do not store your API key."
        )

        base_url = st.text_input(
            "🌐 Base URL (Optional)",
            value=DEFAULT_BASE_URL,
            help="Default is OpenAI. Modify for proxies or other compatible LLM providers."
        )

        model_id = st.text_input(
            "🤖 Model ID (Optional)",
            value=DEFAULT_MODEL_ID,
            help="Default is gpt-4o. Modify for other models."
        )

        st.markdown("---")

        with st.expander("📘 How to Use", expanded=False):
            st.markdown("""
                1.  **Enter API Key** in the sidebar.
                2.  **Add Content Sources:** Upload PDFs or paste text
                3.  **Review Sources:** Check your added sources below the input area.
                4.  **Choose Analyses & Detail Level.**
                5.  **Hit '🚀 Analyze All Sources'** and explore the insights!
            """)

        st.markdown("---")
        st.caption("KnowledgeAgent Pro")

    return api_key, base_url, model_id
