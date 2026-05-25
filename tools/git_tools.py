import subprocess
import logging

logger = logging.getLogger(__name__)

def run_git_command(args):
    """Run an arbitrary git command."""
    try:
        result = subprocess.run(["git"] + args, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e.stderr}")
        return f"Error: {e.stderr}"

def git_log(filepath=None):
    """Get the git log, optionally for a specific file."""
    args = ["log", "-n", "10", "--oneline"]
    if filepath:
        args.append(filepath)
    return run_git_command(args)

def git_commit(message):
    """Stage all changes and commit with the given message."""
    run_git_command(["add", "."])
    return run_git_command(["commit", "-m", message])
