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
            messages.append({
                "role": "user",
                "content": f"For context, the code I am committing is:\n\n{diff}"
            })
            messages.extend(chat_history)
        
        response = self.client.chat.completions.create(
            model="qwen/qwen3.8-27b", # Using a model authorized by this API key
            messages=messages,
            temperature=0.8,
            max_tokens=150
        )

        
        return response.choices[0].message.content.strip()
