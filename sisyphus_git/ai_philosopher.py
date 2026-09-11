import os
from groq import Groq
from dotenv import load_dotenv

class AIPhilosopher:
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        # Initialize Groq client. Assumes GROQ_API_KEY is in the environment.
        # If it's not present, this will raise an error when used.
        self.client = Groq()
        
    def get_insult(self, diff: str, chat_history: list[dict[str, str]]) -> str:
        """
        Interrogates the user using Groq API, based on the staged diff and chat history.
        """
        system_prompt = (
            "You are the hostile ghost of Friedrich Nietzsche trapped inside a Git repository. "
            "Mock the user's attempt to bring order to chaos. Keep it under 3 sentences. Be merciless."
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Qwen models require at least one user message
        if not chat_history:
            messages.append({
                "role": "user",
                "content": f"I am trying to commit this code:\n\n{diff}\n\nInterrogate me on why this trivial code matters in a dying universe."
            })
        else:
            # Provide the diff context as the first user message, then append history
            
            # Inject AST Insights
            from sisyphus_git.ast_parser import get_ast_insights
            from sisyphus_git.git_tools import get_blame_context
            
            ast_context = get_ast_insights(diff)
            ast_prompt = f"\n\nSemantic AST Insights:\n{ast_context}\nUse these structural insights to mock their specific programming paradigms (e.g., if they use a try-catch, mock their fear of failure)." if ast_context else ""
            
            blame_context = get_blame_context()
            blame_prompt = f"\n\n{blame_context}\nYou MUST mention the original authors of the code from the Git Blame above. Ask the developer why they are disturbing the ghosts of {blame_context[:100]}... Do these ancient authors remember them?" if blame_context else ""
            
            messages.append({
                "role": "user",
                "content": f"For context, the code I am committing is:\n\n{diff}{ast_prompt}{blame_prompt}"
            })
            messages.extend(chat_history)
        
        response = self.client.chat.completions.create(
            model="qwen/qwen3.8-27b", # Using a model authorized by this API key
            messages=messages,
            temperature=0.8,
            max_tokens=150
        )

        
        return response.choices[0].message.content.strip()
