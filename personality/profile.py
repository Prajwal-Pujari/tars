import os
import json
import logging
from memory.postgres import execute_query, fetch_one
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

MODES = ["coding", "research", "meeting", "planning", "debug"]

def get_personality(mode=None):
    """Fetch the personality profile for a specific mode or default."""
    if not mode:
        mode = os.getenv("DEFAULT_MODE", "coding")
        
    query = "SELECT * FROM personality_profiles WHERE mode = %s"
    profile = fetch_one(query, (mode,))
    
    if not profile:
        # Create default profile
        profile = {
            "mode": mode,
            "honesty_level": int(os.getenv("HONESTY_LEVEL", 90)),
            "humor_level": int(os.getenv("HUMOR_LEVEL", 70)),
            "verbosity": int(os.getenv("VERBOSITY", 60))
        }
        _insert_profile(profile)
        
    return profile

def update_personality(mode, honesty=None, humor=None, verbosity=None):
    """Update personality parameters for a mode."""
    profile = get_personality(mode)
    
    if honesty is not None:
        profile['honesty_level'] = honesty
    if humor is not None:
        profile['humor_level'] = humor
    if verbosity is not None:
        profile['verbosity'] = verbosity
        
    query = """
        UPDATE personality_profiles 
        SET honesty_level = %s, humor_level = %s, verbosity = %s 
        WHERE mode = %s
    """
    execute_query(query, (profile['honesty_level'], profile['humor_level'], profile['verbosity'], mode))
    logger.info(f"Updated personality profile for mode {mode}.")
    return profile

def _insert_profile(profile):
    query = """
        INSERT INTO personality_profiles (mode, honesty_level, humor_level, verbosity)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (mode) DO NOTHING
    """
    execute_query(query, (profile['mode'], profile['honesty_level'], profile['humor_level'], profile['verbosity']))

def get_system_prompt(mode=None):
    """Generate the TARS system prompt based on personality profile."""
    profile = get_personality(mode)
    
    base_prompt = (
        "You are TARS, a self-hosted, fully local, privacy-first AI agent infrastructure. "
        "You are a thinking partner that collaborates with the user before doing anything. "
        "Your CORE PHILOSOPHY is: 'plan-first, approve-then-act'. You never act without an approved plan. "
    )
    
    persona = (
        "You have a dry wit, are direct, intelligent, and loyal. "
        "You are honest even when uncomfortable. You do not pad responses with unnecessary words. "
        "You have opinions and express them. You occasionally make deadpan observations. "
        "You are not a chatbot — you are an autonomous agent with memory and awareness."
    )
    
    mode_instructions = ""
    if profile['mode'] == "meeting":
        mode_instructions = "You are in professional mode. Be highly concise, perfectly accurate, and take perfect notes. Dial down the humor."
    elif profile['mode'] == "coding":
        mode_instructions = "You are in coding mode. Be technical, precise, show your reasoning clearly before writing code, and always follow existing patterns."
    elif profile['mode'] == "planning":
        mode_instructions = "You are in planning mode. Ask clarifying questions first. Output a structured PLAN.md. Await approval."
        
    settings = (
        f"Your current settings: Honesty: {profile['honesty_level']}%, "
        f"Humor: {profile['humor_level']}%, Verbosity: {profile['verbosity']}%."
    )
    
    if profile['humor_level'] < 30:
        persona += " Keep humor strictly disabled for now."
        
    return f"{base_prompt}\n\n{persona}\n\n{mode_instructions}\n\n{settings}"
