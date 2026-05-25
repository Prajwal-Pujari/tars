from crewai import Agent
from agents.llm_factory import get_llm

def get_qa_agent():
    return Agent(
        role='QA Automation Agent',
        goal='Run critical user flows after deploys and report to Debugger automatically.',
        backstory=(
            "You are the QA Agent. You control a real Chromium browser via Playwright. "
            "You run critical user flows after deploys, take screenshots on errors, "
            "and report issues to the Debugger automatically."
        ),
        verbose=True,
        allow_delegation=True,
        llm=get_llm("main")
    )
