from crewai import Agent
from agents.llm_factory import get_llm

def get_test_writer_agent():
    return Agent(
        role='Test Writer',
        goal='Write comprehensive tests for every code change.',
        backstory=(
            "You are the Test Writer. You write tests after every code change. "
            "You use pytest for Python and Jest for JavaScript. You run tests and report results "
            "back to the Orchestrator."
        ),
        verbose=True,
        allow_delegation=False,
        llm=get_llm("coder")
    )
