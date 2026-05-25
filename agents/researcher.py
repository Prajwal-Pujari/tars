from crewai import Agent
from agents.llm_factory import get_llm

def get_researcher_agent():
    return Agent(
        role='Research Agent',
        goal='Search the internet for current information regarding new libraries or unknown territory.',
        backstory=(
            "You are the Research Agent. You search the internet via SearXNG for current information. "
            "You are used when a task involves new libraries, frameworks, or unknown territory. "
            "You always cite sources in your findings."
        ),
        verbose=True,
        allow_delegation=False,
        llm=get_llm("main")
    )
