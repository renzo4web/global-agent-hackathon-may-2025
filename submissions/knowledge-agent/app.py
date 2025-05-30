import streamlit as st
import asyncio
from agents import create_analysis_team, DEFAULT_MODEL_ID, DEFAULT_BASE_URL

# --- Page Configuration ---
st.set_page_config(
    page_title="KnowledgeAgent Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize Session State ---
if "sources" not in st.session_state:
    st.session_state.sources = []
if "textarea_key_counter" not in st.session_state:
    st.session_state.textarea_key_counter = 0  # Counter for the textarea key

# --- Header ---
st.markdown("<h1 style='text-align: center; color: #333;'>✨ KnowledgeAgent Pro ✨</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #555;'>Unlock Deeper Understanding from Your Content</h3>",
            unsafe_allow_html=True)
st.markdown("---")

# --- Sidebar ---
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
            2.  **Add Content Sources:** Paste text into the main area and click "➕ Add Source". Repeat for all content. The input area will clear after each addition.
            3.  **Review Sources:** Check your added sources below the input area.
            4.  **Choose Analyses & Detail Level.**
            5.  **Hit '🚀 Analyze All Sources'** and explore the insights!
        """)
    st.markdown("---")
    st.caption("KnowledgeAgent Pro")

# --- Main Application Area ---
st.markdown("## 1. Add Your Content Sources")

# Generate a dynamic key for the text_area
current_textarea_key = f"new_source_input_{st.session_state.textarea_key_counter}"

new_source_text_from_widget = st.text_area(
    "Paste your text, article, or any information here:",
    height=200,
    placeholder="Example: A news article, a chapter from a book...",
    key=current_textarea_key  # Dynamic key
)

MAX_SOURCES = 20

if len(st.session_state.sources) < MAX_SOURCES:
    if st.button("➕ Add Source", use_container_width=True, type="secondary"):
        # Read from the text_area using its current dynamic key
        text_to_add = st.session_state.get(current_textarea_key, "").strip()
        if text_to_add:
            source_title = text_to_add[:70] + "..."
            st.session_state.sources.append({"title": source_title, "content": text_to_add})

            # Increment the counter to change the key for the next render
            st.session_state.textarea_key_counter += 1
            st.rerun()  # Force rerun. The text_area will now have a new key and appear empty.
        else:
            st.warning("❗ Please paste some text to add as a source.", icon="⚠️")
elif st.session_state.sources:
    st.info(f"ℹ️ Maximum of {MAX_SOURCES} sources reached. Analyze current sources or remove some to add new ones.",
            icon="ℹ️")

# Display added sources
if st.session_state.sources:
    st.markdown("---")
    st.markdown("### My Content Sources")
    if st.button("🗑️ Clear All Sources", type="secondary", use_container_width=True):
        st.session_state.sources = []
        st.rerun()
    num_columns = min(len(st.session_state.sources), 3)
    if not st.session_state.sources:  # Should not happen if this block is entered, but good for safety
        num_columns = 1

    cols = st.columns(num_columns)


    def remove_source_callback(index_to_remove):  # Callback still good for list manipulation
        if 0 <= index_to_remove < len(st.session_state.sources):
            st.session_state.sources.pop(index_to_remove)


    for index, source in enumerate(st.session_state.sources):
        col_index = index % num_columns
        with cols[col_index]:
            with st.container(border=True):
                st.markdown(f"**Source {index + 1}:** {source['title']}")
                with st.expander("View/Hide Content", expanded=False):
                    # Key for these text_areas can be static or include index, as they are for display
                    st.text_area(f"Content of Source {index + 1}", source['content'], height=150, disabled=True,
                                 key=f"source_content_view_{index}")

                st.button(
                    f"🗑️ Remove Source {index + 1}",
                    key=f"del_source_{index}",  # Static keys for delete buttons are fine here
                    on_click=remove_source_callback,
                    args=(index,),
                    use_container_width=True,
                    type="secondary"
                )
    st.markdown("---")
else:
    st.info("ℹ️ Add content sources using the text area above and the '➕ Add Source' button.", icon="ℹ️")

# --- Analysis Configuration ---
st.markdown("## 2. Configure Your Analysis")
col_options, col_detail = st.columns([2, 1])

with col_options:
    st.markdown("#### Choose Analysis Lenses")
    st.caption("Select types of insights. Hover for details.")
    analysis_options_config = {
        "📄 Summary": {"selected": True, "help": "A concise overview of the main points."},
        "🔍 In-depth Analysis": {"selected": False, "help": "A detailed examination of themes, arguments, and nuances."},
        "🗺️ Concept Map": {"selected": False, "help": "A text-based representation of key concepts and relationships."},
        "🎯 Key Points": {"selected": False, "help": "A bulleted list of the most important takeaways."},
        "📊 SWOT Analysis": {"selected": False, "help": "Identifies Strengths, Weaknesses, Opportunities, and Threats."}
    }
    selected_analysis_keys = [
        name for name, props in analysis_options_config.items() if
        st.checkbox(name, value=props["selected"], help=props["help"])
    ]

with col_detail:
    st.markdown("#### Set Output Detail")
    st.caption("How comprehensive should responses be?")
    output_length = st.radio(
        "Select Detail Level:", options=["Brief", "Standard", "Detailed"], index=1, horizontal=True,
        label_visibility="collapsed"
    )
st.markdown("---")

# --- Action Button ---
if st.button("🚀 Analyze All Sources", type="primary", use_container_width=True,
             help="Analyzes all added content sources together!"):
    if not api_key:
        st.error("❗ API Key Missing: Please enter your OpenAI API key in the sidebar.", icon="🔑")
    elif not st.session_state.sources:
        st.warning("❗ No Sources Added: Please add at least one content source to analyze.", icon="📚")
    elif not selected_analysis_keys:
        st.warning("❗ No Analysis Selected: Please choose at least one analysis type.", icon="🧪")
    else:
        try:
            team = create_analysis_team(api_key, base_url, model_id)
            combined_content = "\n\n--- Source Separator ---\n\n".join(
                [f"Source {i + 1}:\n{s['content']}" for i, s in enumerate(st.session_state.sources)]
            )
            status_message_verb = "analyzing your source" if len(
                st.session_state.sources) == 1 else f"analyzing {len(st.session_state.sources)} combined sources"
            status_message = f"🧠 Your AI team is {status_message_verb} for {len(selected_analysis_keys)} tasks..."

            with st.spinner(status_message):
                async def process_analysis_task(analysis_type_task):
                    prompt = f"""
                    You are analyzing a collection of text sources provided by the user.
                    The sources are concatenated and separated by '--- Source Separator ---'.
                    Each source is also prefixed with "Source X:" to help you differentiate if needed.

                    Analysis type to perform: {analysis_type_task}
                    Desired output detail level: {output_length}

                    Combined text from all sources:
                    {combined_content}
                    """
                    response = await team.arun(prompt)
                    return analysis_type_task, response.content


                async def process_all_tasks():
                    tasks = [process_analysis_task(analysis_type) for analysis_type in selected_analysis_keys]
                    return await asyncio.gather(*tasks)


                results_list = asyncio.run(process_all_tasks())
                results = {res_type: res_content for res_type, res_content in results_list}

            st.success(
                f"🎉 Insights Uncovered! All {len(selected_analysis_keys)} analyses on the combined sources are complete.")
            st.balloons()

            st.markdown("---")
            st.markdown("## 💡 Your Generated Insights (from all sources combined)")
            if results:
                if len(results) > 1:
                    tab_titles = [str(key) for key in results.keys()]
                    tabs = st.tabs(tab_titles)
                    for i, (analysis_type_disp, content_disp) in enumerate(results.items()):
                        with tabs[i]:
                            st.markdown(f"### {analysis_type_disp}")
                            st.markdown(content_disp, unsafe_allow_html=True)
                elif results:
                    analysis_type_single, content_single = list(results.items())[0]
                    st.markdown(f"### {analysis_type_single}")
                    st.markdown(content_single, unsafe_allow_html=True)
            else:
                st.info("It seems no results were generated. Please check your input or try different settings.")

            if results:
                st.markdown("---")
                st.markdown("### 💾 Download Your Insights")


                def create_download_button(label, data, file_name_prefix, key_suffix, use_container_width_dl=False,
                                           is_primary=False):
                    st.download_button(
                        label=label, data=data,
                        file_name=f"{file_name_prefix.lower().replace(' ', '_')}_{key_suffix}.md",
                        mime="text/markdown",
                        key=f"download_{key_suffix.replace(' ', '_')}_{file_name_prefix.replace(' ', '_')}",
                        use_container_width=use_container_width_dl, type="primary" if is_primary else "secondary"
                    )


                if len(results) > 1:
                    all_results_content = "\n\n---\n\n".join(
                        [f"# {res_type_all}\n\n{res_content_all}" for res_type_all, res_content_all in results.items()]
                    )
                    create_download_button(
                        label="📥 Download All Insights (Combined File)", data=all_results_content,
                        file_name_prefix="all_sources_insights", key_suffix="all",
                        use_container_width_dl=True, is_primary=True
                    )
                    st.markdown("---")
                    st.markdown("##### Individual Analysis Downloads:")
                    col_count_dl = min(len(results), 3)
                    cols_dl = st.columns(col_count_dl)
                    for i, (analysis_type_dl, content_dl) in enumerate(results.items()):
                        with cols_dl[i % col_count_dl]:
                            create_download_button(
                                label=f"📄 {analysis_type_dl}", data=content_dl,
                                file_name_prefix=f"all_sources_{str(analysis_type_dl)}",
                                key_suffix=str(analysis_type_dl),
                                use_container_width_dl=True
                            )
                elif selected_analysis_keys:
                    single_analysis_type_dl = selected_analysis_keys[0]
                    create_download_button(
                        label=f"📄 Download {single_analysis_type_dl}", data=list(results.values())[0],
                        file_name_prefix=f"all_sources_{str(single_analysis_type_dl)}", key_suffix="single",
                        use_container_width_dl=True, is_primary=True
                    )
        except Exception as e:
            st.error(f"🚧 An error occurred during analysis: {str(e)}")
            # st.exception(e) # Uncomment for detailed traceback during development
