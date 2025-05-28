import streamlit as st
import asyncio
from agents import create_analysis_team

st.set_page_config(page_title="KnowledgeAgent", page_icon="🧠", layout="wide")

# Title
st.title("🧠 KnowledgeAgent")
st.subheader("AI-Powered Content Analysis Tool")

# Sidebar for API configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("API Key", type="password")
    base_url = st.text_input("Base URL (optional)", value="https://api.openai.com/v1")

# Main content
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("Input Text")
    input_text = st.text_area("Paste your text here", height=300)

with col2:
    st.subheader("Analysis Types")
    st.caption("Select one or more")

    summary = st.checkbox("📄 Summary", value=True)
    analysis = st.checkbox("🔍 Analysis")
    concept_map = st.checkbox("🗺️ Concept Map")
    key_points = st.checkbox("🎯 Key Points")
    swot = st.checkbox("📊 SWOT Analysis")

    # Collect selected types
    selected_types = []
    if summary: selected_types.append("Summary")
    if analysis: selected_types.append("Analysis")
    if concept_map: selected_types.append("Concept Map")
    if key_points: selected_types.append("Key Points")
    if swot: selected_types.append("SWOT")

    st.divider()

    output_length = st.select_slider(
        "Length",
        ["Brief", "Standard", "Detailed"],
        value="Standard"
    )

# Process button
if st.button("🚀 Analyze", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please enter your API key")
    elif not input_text:
        st.error("Please enter some text")
    elif not selected_types:
        st.error("Please select at least one analysis type")
    else:
        # Create team once
        team = create_analysis_team(api_key, base_url)

        # Show loading message
        with st.spinner(f"Processing {len(selected_types)} analyses in parallel..."):
            # Async function to process single analysis
            # TODO: move to another file util
            async def process_analysis(analysis_type):
                prompt = f"""
                Analysis type: {analysis_type}
                Output length: {output_length}

                Text to analyze:
                {input_text}
                """

                # Get response
                response = await team.arun(prompt)
                return analysis_type, response.content


            # Process all analyses in parallel
            async def process_all():
                tasks = [process_analysis(analysis_type) for analysis_type in selected_types]
                return await asyncio.gather(*tasks)


            # Run all analyses
            results_list = asyncio.run(process_all())
            results = {analysis_type: content for analysis_type, content in results_list}

        # Display results
        st.success(f"✅ All {len(selected_types)} analyses completed!")

        # Create tabs if multiple analyses
        if len(results) > 1:
            tabs = st.tabs(selected_types)
            for i, (analysis_type, content) in enumerate(results.items()):
                with tabs[i]:
                    st.markdown(content)
        else:
            # Single result
            st.markdown(list(results.values())[0])

        # Add download buttons
        st.divider()

        if len(results) > 1:
            # Download individual results
            col_count = min(len(results), 3)
            cols = st.columns(col_count)
            for i, (analysis_type, content) in enumerate(results.items()):
                with cols[i % col_count]:
                    st.download_button(
                        f"📥 {analysis_type}",
                        content,
                        f"{analysis_type.lower().replace(' ', '_')}.md",
                        "text/markdown",
                        key=f"download_{analysis_type}"
                    )

            # Download all results
            all_results = "\n\n---\n\n".join([
                f"# {analysis_type}\n\n{content}"
                for analysis_type, content in results.items()
            ])
            st.download_button(
                "📥 Download All Results",
                all_results,
                "all_analysis.md",
                "text/markdown",
                type="primary",
                use_container_width=True
            )
        else:
            # Single result
            analysis_type = selected_types[0]
            st.download_button(
                "📥 Download",
                results[analysis_type],
                f"{analysis_type.lower().replace(' ', '_')}.md",
                "text/markdown"
            )

