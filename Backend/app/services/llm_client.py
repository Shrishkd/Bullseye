# app/services/llm_client.py

import os
from google import genai


class LLMClient:
    """
    Gemini-based LLM client for Bullock.
    Uses the modern `google-genai` SDK (recommended by Google).
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            self.client = None
            return

        # Initialize Gemini client
        self.client = genai.Client(api_key=api_key)

        # Default model (fast + cost-efficient)
        self.model_name = "gemini-1.5-flash"

    def chat(self, system_prompt: str, user_message: str) -> str:
        """
        Generate an AI response using Gemini.

        Parameters:
        - system_prompt: Instructions / role definition
        - user_message: User question + context

        Returns:
        - Generated text response
        """

        if not self.client:
            return "Gemini API key not configured."

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"""
{system_prompt}

{user_message}
""",
                generation_config={
                    "temperature": 0.4,
                    "max_output_tokens": 512,
                },
            )

            return response.text.strip() if response.text else "No response generated."

        except Exception as e:
            # Never crash the app because of AI
            return f"AI service error: {str(e)}"
