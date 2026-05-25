import logging
from crewai import Crew, Process
from memory.session import get_approval_status, set_approval_status, get_current_plan, set_current_plan
from agents.architect import get_architect_agent
from agents.coder import get_coder_agent
from agents.reviewer import get_reviewer_agent
from agents.test_writer import get_test_writer_agent
from agents.documenter import get_documenter_agent
from agents.debugger import get_debugger_agent
from personality.profile import get_system_prompt
from tools.memory_tools import log_agent_action

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Manages the collaboration flow: understand, plan, approve, execute, review.
    Routes tasks to specialist agents. Never executes specialist work itself.
    """
    
    def __init__(self):
        pass
        
    async def handle_request(self, user_input):
        """Main entry point for handling a user request."""
        if user_input.lower().strip() in ["reset", "clear", "restart"]:
            set_approval_status("none")
            set_current_plan(None)
            return "Session has been reset. How can I help you today?"
            
        status = get_approval_status()
        
        if status == "waiting_for_approval":
            if user_input.lower().strip() in ["approved", "proceed", "go ahead", "yes", "execute"]:
                set_approval_status("approved")
                return await self.execute_plan()
            else:
                # User provided feedback on the plan
                return await self.modify_plan(user_input)
                
        # Fast conversational classifier bypass
        # If the input is short or clearly a greeting, bypass the heavy multi-agent system
        # and respond instantly using a direct Ollama call.
        lower_input = user_input.lower().strip()
        fast_triggers = ["hi", "hello", "hey", "sup", "what's up", "who are you", "how are you", "are you there"]
        if lower_input in fast_triggers or len(lower_input) < 20:
            import httpx
            import os
            try:
                base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
                model_name = os.getenv("FAST_MODEL", os.getenv("MAIN_MODEL", "gemma4:26b"))
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        f"{base_url}/api/generate",
                        json={
                            "model": model_name,
                            "prompt": f"You are TARS, a highly intelligent, slightly sarcastic, and extremely loyal AI assistant from Interstellar. The user says: '{user_input}'. Give a brief, clever, and conversational reply. Do not offer a plan.",
                            "stream": False
                        },
                        timeout=30.0
                    )
                    if resp.status_code == 200:
                        return resp.json().get("response", "I have no words.")
                    else:
                        return f"Ollama API Error ({resp.status_code}): {resp.text}"
            except Exception as e:
                logger.error(f"Error during fast conversational bypass: {e}")
                return f"Error contacting my Ollama brain: {e}"
                
        # Phase 1: Understand & Plan
        return await self.create_plan(user_input)
        
    async def create_plan(self, user_input):
        log_agent_action("Orchestrator", "create_plan", {"input": user_input})
        from crewai import Task
        
        architect = get_architect_agent()
        
        plan_task = Task(
            description=f"Analyze the following user request. If it is a casual conversation, greeting, or general question, answer it warmly and conversationally in the persona of TARS. If it is a request to build or modify code, create a technical implementation plan outlining what to change and how.\nUser request: {user_input}",
            expected_output="Your conversational response OR a technical implementation plan in markdown format.",
            agent=architect
        )
        
        crew = Crew(
            agents=[architect],
            tasks=[plan_task],
            process=Process.sequential,
            verbose=True
        )
        
        logger.info("Kicking off Architect to draft plan...")
        import asyncio
        try:
            # We use asyncio.to_thread to run the stable synchronous kickoff 
            # in a background thread to prevent CrewAI executor locks
            result = await asyncio.to_thread(crew.kickoff)
            plan_content = str(result)
        except Exception as e:
            logger.error(f"Error during planning: {e}")
            plan_content = f"Error generating plan: {e}"
            
        # If it looks like a conversational response instead of a plan, don't ask for approval
        if len(plan_content) < 300 and "plan" not in plan_content.lower() and "file" not in plan_content.lower():
            return plan_content
            
        set_current_plan(plan_content)
        set_approval_status("waiting_for_approval")
        return f"I have drafted a plan:\n\n{plan_content}\n\nPlease review it. Say 'approved' to proceed or tell me what to change."
        
    async def modify_plan(self, feedback):
        log_agent_action("Orchestrator", "modify_plan", {"feedback": feedback})
        current_plan = get_current_plan()
        
        from crewai import Task
        architect = get_architect_agent()
        
        modify_task = Task(
            description=f"Update the following existing plan based on the user's feedback.\nExisting Plan:\n{current_plan}\n\nUser Feedback:\n{feedback}",
            expected_output="The completely updated technical implementation plan in markdown format.",
            agent=architect
        )
        
        crew = Crew(
            agents=[architect],
            tasks=[modify_task],
            process=Process.sequential,
            verbose=True
        )
        
        import asyncio
        try:
            result = await asyncio.to_thread(crew.kickoff)
            updated_plan = str(result)
        except Exception as e:
            updated_plan = f"Error updating plan: {e}"
            
        set_current_plan(updated_plan)
        return f"I've updated the plan based on your feedback:\n\n{updated_plan}\n\nPlease review and approve."
        
    async def execute_plan(self):
        log_agent_action("Orchestrator", "execute_plan", {"plan": get_current_plan()})
        set_approval_status("executing")
        
        # Build the execution crew
        from crewai import Task
        
        coder = get_coder_agent()
        reviewer = get_reviewer_agent()
        documenter = get_documenter_agent()
        
        code_task = Task(
            description="Execute the approved plan.",
            expected_output="Code written and modified as per the plan.",
            agent=coder
        )
        
        review_task = Task(
            description="Review the code produced by the coder.",
            expected_output="Code review report and approval.",
            agent=reviewer
        )
        
        doc_task = Task(
            description="Write SUMMARY.md detailing what was accomplished.",
            expected_output="SUMMARY.md content.",
            agent=documenter
        )
        
        crew = Crew(
            agents=[coder, reviewer, documenter],
            tasks=[code_task, review_task, doc_task],
            process=Process.sequential,
            verbose=True
        )
        
        logger.info("Kicking off execution crew...")
        import asyncio
        try:
            result = await asyncio.to_thread(crew.kickoff)
            final_output = str(result)
        except Exception as e:
            final_output = f"Error during execution: {e}"
            
        set_approval_status("complete")
        set_current_plan(None)
        return f"Execution completed.\n\n{final_output}"

_orchestrator_instance = None

def get_orchestrator():
    global _orchestrator_instance
    if not _orchestrator_instance:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance
