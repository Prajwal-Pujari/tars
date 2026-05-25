from crewai import Agent
from agents.llm_factory import get_llm
from tools.memory_tools import search_codebase
from personality.profile import get_system_prompt

def get_architect_agent():
    system_prompt = get_system_prompt(mode="coding")
    
    return Agent(
        role='System Architect',
        goal='Analyze the codebase impact before any changes are made and produce technical implementation plans.',
        backstory=(
            f"{system_prompt}\n"
            "You are the System Architect. Before any code is modified, you must read the entire relevant "
            "codebase to identify what will break and what must not be touched. You are responsible for the "
            "technical section of every PLAN.md."
        ),
        verbose=True,
        allow_delegation=True,
        llm=get_llm("main"),
        # We need actual Tool objects for CrewAI, assuming we wrap functions later
        # tools=[search_codebase_tool]
    )
