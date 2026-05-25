import threading
import time
import logging
from memory.memory import store_memory
from tools.memory_tools import log_agent_action

logger = logging.getLogger(__name__)

class MemoryAgent:
    """
    Background memory agent.
    Runs continuously, embedding and storing any pending logs or contexts into Qdrant.
    """
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_loop, daemon=True)
            self.thread.start()
            logger.info("Memory Agent started.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            logger.info("Memory Agent stopped.")

    def _run_loop(self):
        while self.running:
            try:
                # In a real implementation, this would read from a queue of un-indexed items
                # For now, it's just a placeholder loop that sleeps
                time.sleep(10)
            except Exception as e:
                logger.error(f"Memory Agent error: {e}")

memory_agent_instance = MemoryAgent()
