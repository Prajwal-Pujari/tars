import os
import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from indexer.indexer import index_file

logger = logging.getLogger(__name__)

class CodeEventHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.valid_extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.rs', '.go']
        self.ignore_paths = ['venv', '.git', '__pycache__', 'node_modules']

    def _should_process(self, path):
        # Check extensions
        ext = os.path.splitext(path)[1]
        if ext not in self.valid_extensions:
            return False
            
        # Check ignored directories
        for ignored in self.ignore_paths:
            if f"/{ignored}/" in path.replace('\\', '/') or path.endswith(ignored):
                return False
                
        return True

    def on_modified(self, event):
        if not event.is_directory and self._should_process(event.src_path):
            logger.info(f"File modified: {event.src_path}. Re-indexing...")
            # Small delay to ensure file write is complete
            time.sleep(0.5)
            index_file(event.src_path)
            
    def on_created(self, event):
        if not event.is_directory and self._should_process(event.src_path):
            logger.info(f"File created: {event.src_path}. Indexing...")
            time.sleep(0.5)
            index_file(event.src_path)

def start_watcher(path="."):
    """Start the watchdog observer."""
    event_handler = CodeEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    logger.info(f"Started file watcher on {os.path.abspath(path)}")
    return observer
