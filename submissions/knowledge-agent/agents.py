from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.team import Team


def create_analysis_team(api_key: str, base_url: str = "https://api.openai.com/v1", model_id: str = "gpt-4o"):
    """Create a team of analysis agents"""

    # Create model
    model = OpenAILike(
        id=model_id,
        api_key=api_key,
        base_url=base_url
    )

    # Create specialized agents
    summarizer = Agent(
        name="Summarizer",
        role="Creates concise summaries of text content",
        model=model,
        instructions=["Focus on key points", "Be concise and clear"],
        markdown=True
    )

    analyzer = Agent(
        name="Analyzer",
        role="Provides detailed analysis of content",
        model=model,
        instructions=["Identify patterns and themes", "Provide insights and implications"],
        markdown=True
    )

    concept_mapper = Agent(
        name="Concept Mapper",
        role="Creates conceptual relationships and mind maps",
        model=model,
        instructions=["Identify main concepts", "Show relationships between ideas"],
        markdown=True
    )

    key_points_extractor = Agent(
        name="Key Points Extractor",
        role="Extracts bullet-point key information",
        model=model,
        instructions=["List the most important points", "Use clear bullet points"],
        markdown=True
    )

    swot_analyst = Agent(
        name="SWOT Analyst",
        role="Performs SWOT analysis (Strengths, Weaknesses, Opportunities, Threats)",
        model=model,
        instructions=["Identify SWOT elements", "Provide balanced analysis"],
        markdown=True
    )

    # Create team
    team = Team(
        name="Analysis Team",
        mode="coordinate",
        model=model,
        members=[summarizer, analyzer, concept_mapper, key_points_extractor, swot_analyst],
        instructions=[
            "Route the request to the appropriate team member based on the analysis type",
            "Ensure the output matches the requested length (Brief/Standard/Detailed)",
            "Format all responses in clean markdown"
        ],
        markdown=True,
        debug_mode=True
    )

    return team
