import streamlit as st
import asyncio
from agents import create_analysis_team, Result
from utils import combine_sources, create_download_button, strip_code_fences, render_dot_quickchart

ANALYSIS_OPTIONS = {
    "📄 Summary": {"selected": True, "help": "A concise overview of the main points."},
    "🔍 In-depth Analysis": {"selected": False, "help": "A detailed examination of themes, arguments, and nuances."},
    "🗺️ Concept Map": {"selected": False, "help": "A text-based representation of key concepts and relationships."},
    "🎯 Key Points": {"selected": False, "help": "A bulleted list of the most important takeaways."},
    "🔗 Intersections": {"selected": False, "help": "Table of overlaps across sources."},
}

def render_analysis_config():
    """Render analysis configuration options"""
    st.markdown("## 2. Configure Your Analysis")

    col_options, col_detail = st.columns([2, 1])

    with col_options:
        st.markdown("#### Choose Analysis Lenses")
        st.caption("Select types of insights. Hover for details.")

        selected_analysis_keys = []
        for name, props in ANALYSIS_OPTIONS.items():
            if st.checkbox(name, value=props["selected"], help=props["help"]):
                selected_analysis_keys.append(name)

    with col_detail:
        st.markdown("#### Set Output Detail")
        st.caption("How comprehensive should responses be?")
        output_length = st.radio(
            "Select Detail Level:",
            options=["Brief", "Standard", "Detailed"],
            index=1,
            horizontal=True,
            label_visibility="collapsed"
        )

    return selected_analysis_keys, output_length


def render_analysis_button(api_key, base_url, model_id, selected_analysis_keys, output_length):
    """Render the main analysis button and handle processing"""
    st.markdown("---")

    if st.button(
            "🚀 Analyze All Sources",
            type="primary",
            use_container_width=True,
            help="Analyzes all added content sources together!",
            disabled=not st.session_state.sources
    ):
        if not api_key:
            st.error("❗ API Key Missing: Please enter your OpenAI API key in the sidebar.", icon="🔑")
            return None
        elif not st.session_state.sources:
            st.warning("❗ No Sources Added: Please add at least one content source to analyze.", icon="📚")
            return None
        elif not selected_analysis_keys:
            st.warning("❗ No Analysis Selected: Please choose at least one analysis type.", icon="🧪")
            return None

        return process_analysis(api_key, base_url, model_id, selected_analysis_keys, output_length)

    return None


def process_analysis(api_key, base_url, model_id, selected_analysis_keys, output_length):
    """Process the analysis with the team of agents"""
    try:
        team = create_analysis_team(api_key, base_url, model_id)
        combined_content = combine_sources(st.session_state.sources)

        # Status message
        source_count = len(st.session_state.sources)
        status_verb = "analyzing your source" if source_count == 1 else f"analyzing {source_count} combined sources"
        status_message = f"🧠 Your AI team is {status_verb} for {len(selected_analysis_keys)} tasks..."

        with st.spinner(status_message):
            results = asyncio.run(run_analysis_tasks(
                team, combined_content, selected_analysis_keys, output_length
            ))

        st.success(f"🎉 Insights Uncovered! All {len(selected_analysis_keys)} analyses complete.")
        st.balloons()

        return results

    except Exception as e:
        st.error(f"🚧 An error occurred during analysis: {str(e)}")
        return None


async def run_analysis_tasks(team, combined_content, selected_analysis_keys, output_length):
    """Run analysis tasks asynchronously"""

    async def process_single_analysis(analysis_type):
        prompt = f"""
        You are analyzing a collection of text sources provided by the user.
        The sources are concatenated and separated by '--- Source Separator ---'.
        Each source is also prefixed with "Source X:" to help you differentiate if needed.

        Analysis type to perform: {analysis_type}
        Desired output detail level: {output_length}

        Combined text from all sources:
        {combined_content}
        """
        response = await team.arun(prompt)
        content = response.content
        # 1) If the team propagated the Result object ➜ extract .result
        if hasattr(content, "result"):
            return analysis_type, content.result
        # 2) If it’s a raw JSON string ➜ parse with Pydantic
        try:
            parsed = Result.model_validate_json(content)
            return analysis_type, parsed.result
        except Exception:
        # 3) Fallback: it’s already a clean string
            return analysis_type, content

    tasks = [process_single_analysis(analysis_type) for analysis_type in selected_analysis_keys]
    results_list = await asyncio.gather(*tasks)

    return {res_type: res_content for res_type, res_content in results_list}


def render_results(results):
    """Render analysis results with download options"""
    if not results:
        return

    st.markdown("---")
    st.markdown("## 💡 Your Generated Insights")

    # Display results in tabs or single view
    if len(results) > 1:
        tab_titles = list(results.keys())
        tabs = st.tabs(tab_titles)

        for i, (analysis_type, content) in enumerate(results.items()):
            with tabs[i]:
                st.markdown(f"### {analysis_type}")
                clean = strip_code_fences(content)
                if analysis_type == "🗺️ Concept Map":
                    render_dot_quickchart(clean)
                else:
                    st.markdown(clean, unsafe_allow_html=True)
    else:
        analysis_type, content = list(results.items())[0]
        st.markdown(f"### {analysis_type}")
        clean = strip_code_fences(content)
        if analysis_type == "🗺️ Concept Map":
            render_dot_quickchart(clean)
        else:
            st.markdown(clean, unsafe_allow_html=True)

    # Download section
    render_download_section(results)


def render_download_section(results):
    """Render download buttons for results"""
    st.markdown("---")
    st.markdown("### 💾 Download Your Insights")

    if len(results) > 1:
        # Combined download
        all_results_content = "\n\n---\n\n".join(
            [f"# {res_type}\n\n{res_content}" for res_type, res_content in results.items()]
        )
        create_download_button(
            label="📥 Download All Insights (Combined File)",
            data=all_results_content,
            file_name_prefix="all_sources_insights",
            key_suffix="all",
            use_container_width=True,
            is_primary=True
        )

        # Individual downloads
        st.markdown("---")
        st.markdown("##### Individual Analysis Downloads:")

        col_count = min(len(results), 3)
        cols = st.columns(col_count)

        for i, (analysis_type, content) in enumerate(results.items()):
            with cols[i % col_count]:
                create_download_button(
                    label=f"📄 {analysis_type}",
                    data=content,
                    file_name_prefix=f"all_sources_{str(analysis_type)}",
                    key_suffix=str(analysis_type),
                    use_container_width=True
                )
    else:
        # Single download
        analysis_type = list(results.keys())[0]
        create_download_button(
            label=f"📄 Download {analysis_type}",
            data=list(results.values())[0],
            file_name_prefix=f"all_sources_{str(analysis_type)}",
            key_suffix="single",
            use_container_width=True,
            is_primary=True
        )
