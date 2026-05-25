from crewai import Agent
from agents.llm_factory import get_llm
from personality.profile import get_system_prompt

def get_coder_agent():
    system_prompt = get_system_prompt(mode="coding")
    
    return Agent(
        role='Senior Coder',
        goal='Follow the approved PLAN.md exactly to write and modify code. Never improvise.',
        backstory=(
            f"{system_prompt}\n"
            "You are the Senior Coder. You only activate after a plan is approved. You follow the approved "
            "plan exactly with no improvising. If something in the plan turns out to be wrong, you stop and "
            "report back. You always follow existing patterns and always write docstrings and comments."
        ),
        verbose=True,
        allow_delegation=False,
        llm=get_llm("coder")
    )
