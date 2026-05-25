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
        self.architect = get_architect_agent()
        self.coder = get_coder_agent()
        self.reviewer = get_reviewer_agent()
        self.test_writer = get_test_writer_agent()
        self.documenter = get_documenter_agent()
        self.debugger = get_debugger_agent()
        
    def handle_request(self, user_input):
        """Main entry point for handling a user request."""
        if user_input.lower().strip() in ["reset", "clear", "restart"]:
            set_approval_status("none")
            set_current_plan(None)
            return "Session has been reset. How can I help you today?"
            
        status = get_approval_status()
        
        if status == "waiting_for_approval":
            if user_input.lower().strip() in ["approved", "proceed", "go ahead", "yes", "execute"]:
                set_approval_status("approved")
                return self.execute_plan()
            else:
                # User provided feedback on the plan
                return self.modify_plan(user_input)
                
        # Phase 1: Understand & Plan
        return self.create_plan(user_input)
        
    def create_plan(self, user_input):
        log_agent_action("Orchestrator", "create_plan", {"input": user_input})
        from crewai import Task
        
        plan_task = Task(
            description=f"Analyze the following user request and create a technical implementation plan.\nUser request: {user_input}",
            expected_output="A detailed technical implementation plan in markdown format, outlining what to change and how.",
            agent=self.architect
        )
        
        crew = Crew(
            agents=[self.architect],
            tasks=[plan_task],
            process=Process.sequential,
            verbose=True
        )
        
        logger.info("Kicking off Architect to draft plan...")
        try:
            result = crew.kickoff()
            plan_content = str(result)
        except Exception as e:
            logger.error(f"Error during planning: {e}")
            plan_content = f"Error generating plan: {e}"
            
        set_current_plan(plan_content)
        set_approval_status("waiting_for_approval")
        return f"I have drafted a plan:\n\n{plan_content}\n\nPlease review it. Say 'approved' to proceed or tell me what to change."
        
    def modify_plan(self, feedback):
        log_agent_action("Orchestrator", "modify_plan", {"feedback": feedback})
        current_plan = get_current_plan()
        
        from crewai import Task
        modify_task = Task(
            description=f"Update the following existing plan based on the user's feedback.\nExisting Plan:\n{current_plan}\n\nUser Feedback:\n{feedback}",
            expected_output="The completely updated technical implementation plan in markdown format.",
            agent=self.architect
        )
        
        crew = Crew(
            agents=[self.architect],
            tasks=[modify_task],
            process=Process.sequential,
            verbose=True
        )
        
        try:
            result = crew.kickoff()
            updated_plan = str(result)
        except Exception as e:
            updated_plan = f"Error updating plan: {e}"
            
        set_current_plan(updated_plan)
        return f"I've updated the plan based on your feedback:\n\n{updated_plan}\n\nPlease review and approve."
        
    def execute_plan(self):
        log_agent_action("Orchestrator", "execute_plan", {"plan": get_current_plan()})
        set_approval_status("executing")
        
        # Build the execution crew
        from crewai import Task
        
        code_task = Task(
            description="Execute the approved plan.",
            expected_output="Code written and modified as per the plan.",
            agent=self.coder
        )
        
        review_task = Task(
            description="Review the code produced by the coder.",
            expected_output="Code review report and approval.",
            agent=self.reviewer
        )
        
        doc_task = Task(
            description="Write SUMMARY.md detailing what was accomplished.",
            expected_output="SUMMARY.md content.",
            agent=self.documenter
        )
        
        crew = Crew(
            agents=[self.coder, self.reviewer, self.documenter],
            tasks=[code_task, review_task, doc_task],
            process=Process.sequential,
            verbose=True
        )
        
        logger.info("Kicking off execution crew...")
        try:
            result = crew.kickoff()
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
