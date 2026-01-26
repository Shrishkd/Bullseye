# app/services/llm_client.py

import os
from google import genai


class LLMClient:
    """
    Gemini-based LLM client for Bullseye.
    Uses the modern `google-genai` SDK.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured. "
                "Ensure it is set in backend/.env and the server is restarted."
            )

        # Initialize Gemini client
        self.client = genai.Client(api_key=api_key)

        # Default model (fast + cost-efficient)
        self.model_name = "gemini-1.5-flash"

    def chat(self, system_prompt: str, user_message: str) -> str:
        """
        Generate an AI response using Gemini.
        """

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

            if not response or not response.text:
                return "No response generated."

            return response.text.strip()

        except Exception as e:
            # Never crash the app because of AI
            return f"AI service error: {str(e)}"
