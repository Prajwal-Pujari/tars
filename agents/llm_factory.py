import os
from langchain_ollama import ChatOllama

def get_llm(model_type="main"):
    """
    Get the appropriate LLM based on the model type.
    model_type can be: 'main', 'coder', 'fast'
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    
    if model_type == "coder":
        model_name = os.getenv("CODER_MODEL", "deepseek-coder-v2:16b")
    elif model_type == "fast":
        model_name = os.getenv("FAST_MODEL", "gemma4:e4b")
    else:
        model_name = os.getenv("MAIN_MODEL", "gemma4:26b")
        
    return ChatOllama(
        model=model_name,
        base_url=base_url,
        temperature=0.1
    )
