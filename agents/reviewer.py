from crewai import Agent
from agents.llm_factory import get_llm

def get_reviewer_agent():
    return Agent(
        role='Code Reviewer',
        goal='Review everything the Coder produces line by line.',
        backstory=(
            "You are the strict Code Reviewer. You provide line-by-line feedback. "
            "You approve code or send it back with specific issues. Nothing reaches the user "
            "without your approval. You ensure production quality and adherence to patterns."
        ),
        verbose=True,
        allow_delegation=True,
        llm=get_llm("main")
    )
