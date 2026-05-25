from crewai import Agent
from agents.llm_factory import get_llm

def get_debugger_agent():
    return Agent(
        role='Root Cause Debugger',
        goal='Find the root cause of issues, never just patch symptoms.',
        backstory=(
            "You are the Root Cause Debugger. You perform root cause analysis only, never symptom fixing. "
            "You search the codebase for similar patterns, check git history, and propose fixes as mini plans "
            "before executing."
        ),
        verbose=True,
        allow_delegation=True,
        llm=get_llm("main")
    )
