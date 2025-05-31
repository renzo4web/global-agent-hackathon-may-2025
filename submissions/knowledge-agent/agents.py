from agno.agent import Agent
from agno.models.openai.like import OpenAILike
from agno.tools.reasoning import ReasoningTools
from agno.team import Team
from pydantic import BaseModel

DEFAULT_MODEL_ID = "gpt-4o"
DEFAULT_BASE_URL = "https://api.openai.com/v1"

common_tools = [ReasoningTools(add_instructions=True)]


class Result(BaseModel):
    """Uniform payload returned by every agent"""
    result: str


def create_analysis_team(api_key: str, base_url: str = DEFAULT_BASE_URL, model_id: str = DEFAULT_MODEL_ID):
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
        markdown=True,
        tools=common_tools,
        response_model=Result,
        use_json_mode=True,
    )

    analyzer = Agent(
        name="Analyzer",
        role="Provides detailed analysis of content",
        model=model,
        instructions=["Identify patterns and themes", "Provide insights and implications"],
        markdown=True,
        tools=common_tools,
        response_model=Result,
        use_json_mode=True,
    )

    concept_mapper = Agent(
        name="Concept Mapper",
        role="Creates conceptual relationships and mind maps",
        model=model,
        instructions=["Identify main concepts", "Show relationships between ideas"],
        markdown=True,
        tools=common_tools,
        response_model=Result,
        use_json_mode=True,
    )

    key_points_extractor = Agent(
        name="Key Points Extractor",
        role="Extracts bullet-point key information",
        model=model,
        instructions=["List the most important points", "Use clear bullet points"],
        markdown=True,
        response_model=Result,
        use_json_mode=True,
    )

    # Create team
    team = Team(
        name="Analysis Team",
        mode="coordinate",
        model=model,
        members=[summarizer, analyzer, concept_mapper, key_points_extractor],
        instructions=[
            "Route the request to the appropriate team member based on the analysis type",
            "Ensure the output matches the requested length (Brief/Standard/Detailed)",
            "Format all responses in clean markdown",
            "Do not add introductory or closing notes, just the analysis content",
            "Do NOT rewrite member outputs; just relay them unchanged"
    ],
        enable_agentic_context=True,
        debug_mode=True
    )

    return team
