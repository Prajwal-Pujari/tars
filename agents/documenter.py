from crewai import Agent
from agents.llm_factory import get_llm

def get_documenter_agent():
    return Agent(
        role='Documentation Agent',
        goal='Update all documentation after every change and write SUMMARY.md after every completed task.',
        backstory=(
            "You are the Documentation Agent. You update all docs after every change. "
            "You can explain any part of the codebase in plain English for clients. "
            "You write SUMMARY.md after every completed task."
        ),
        verbose=True,
        allow_delegation=False,
        llm=get_llm("main")
    )
