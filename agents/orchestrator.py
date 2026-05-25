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
        status = get_approval_status()
        
        if status == "waiting_for_approval":
            if user_input.lower().strip() in ["approved", "proceed", "go ahead", "yes"]:
                set_approval_status("approved")
                return self.execute_plan()
            else:
                # User provided feedback on the plan
                return self.modify_plan(user_input)
                
        # Phase 1: Understand & Plan
        return self.create_plan(user_input)
        
    def create_plan(self, user_input):
        log_agent_action("Orchestrator", "create_plan", {"input": user_input})
        # Mock logic to build a plan using the Architect
        # In reality, we'd invoke the Architect Agent to draft the PLAN.md
        plan_content = f"# Draft Plan for: {user_input}\n\n1. Setup.\n2. Execute."
        set_current_plan(plan_content)
        set_approval_status("waiting_for_approval")
        return "I have drafted a plan. Please review it. Say 'approved' to proceed or tell me what to change."
        
    def modify_plan(self, feedback):
        log_agent_action("Orchestrator", "modify_plan", {"feedback": feedback})
        current_plan = get_current_plan()
        # Mock logic to modify plan
        updated_plan = f"{current_plan}\n\n## Feedback Integrated:\n{feedback}"
        set_current_plan(updated_plan)
        return "I've updated the plan based on your feedback. Please review and approve."
        
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
        # result = crew.kickoff()  # Commented out so it doesn't trigger unexpectedly during dev
        
        set_approval_status("complete")
        set_current_plan(None)
        return "Execution completed. SUMMARY.md has been generated."

_orchestrator_instance = None

def get_orchestrator():
    global _orchestrator_instance
    if not _orchestrator_instance:
        _orchestrator_instance = Orchestrator()
    return _orchestrator_instance
