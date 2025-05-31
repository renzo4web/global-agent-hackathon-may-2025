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
        role="Builds a concept graph",
        model=model,
        tools=common_tools,
        response_model=Result,
        use_json_mode=True,
        expected_output="digraph {",
        instructions=[
            "Return ONLY GraphViz DOT that starts with `digraph {` and ends with `}`.",
            "Use lines like `A -> B;` for edges.",
            "Do NOT wrap the code in back-ticks. No explanations."
        ],
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

    intersection_finder = Agent(
        name="Intersection Finder",
        role="Finds entities / claims mentioned by at least two sources",
        model=model,
        tools=common_tools,
        response_model=Result,
        use_json_mode=True,
        instructions=[
            "Return a markdown table where rows are items and columns are Source 1, Source 2, ...",
            "DO NOT add backticks in the beginning of the table. Just the table.",
            "Mark a ✓ when the item appears in that source.",
            "Limit to the 15 most frequent items, ordered by number of sources.",
        ],
    )

    coverage_agent = Agent(
        name="Coverage Analyst",
        role="Builds a source-by-topic coverage matrix",
        model=model,
        tools=common_tools,
        response_model=Result,
        use_json_mode=True,
        instructions=[
              "Extract up to 10 sub-topics"
              "Produce CSV whose first row is: Topic,Source 1,Source 2,..."
              "Put ✓ under a source if the topic appears there, else blank"
              "Return ONLY the CSV – no prose, no backticks"
        ],
    )

    # Create team
    team = Team(
        name="Analysis Team",
        mode="coordinate",
        model=model,
        members=[summarizer, analyzer, concept_mapper, key_points_extractor, intersection_finder, coverage_agent],
        instructions=[
            "Route the request to the appropriate team member based on the analysis type",
            "Ensure the output matches the requested length (Brief/Standard/Detailed)",
            "Do not add introductory or closing notes, just the analysis content",
            "Do NOT rewrite member outputs; just relay them unchanged",
            "NEVER wrap your final answer in triple back-ticks."
    ],
        enable_agentic_context=True,
        debug_mode=True
    )

    return team
