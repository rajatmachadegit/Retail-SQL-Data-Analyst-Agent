# import requests
# from src.config import TIGER_AI_GATEWAY_URL, TIGER_AI_GATEWAY_API_KEY, TIGER_AI_GATEWAY_MODEL

# class TigerGatewayClient:
#     """A client to communicate directly with the Tiger AI Gateway using HTTP requests."""

#     def __init__(self):
#         # Format endpoint to OpenAI Chat Completions standard
#         self.api_url = f"{TIGER_AI_GATEWAY_URL.rstrip('/')}/v1/chat/completions"
#         self.api_key = TIGER_AI_GATEWAY_API_KEY
#         self.model = TIGER_AI_GATEWAY_MODEL

#     def generate_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
#         """Sends a request to the LLM gateway and returns the text response."""
#         if not self.api_key:
#             raise ValueError("TIGER_AI_GATEWAY_API_KEY is not defined in your environment (.env file).")
#         if not self.model:
#             raise ValueError("TIGER_AI_GATEWAY_MODEL is not defined in your environment (.env file).")

#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json"
#         }

#         # Build payload with system parameters and chat history context
#         payload = {
#             "model": self.model,
#             "messages": [
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": user_prompt}
#             ],
#             "temperature": temperature
#         }

#         try:
#             response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
#             response.raise_for_status()

#             # Extract content from the OpenAI-style response JSON structure
#             response_data = response.json()
#             return response_data["choices"][0]["message"]["content"].strip()

#         except requests.exceptions.HTTPError as http_err:
#             raise RuntimeError(f"Tiger AI Gateway HTTP Error: {http_err} - Details: {response.text}")
#         except Exception as err:
#             raise RuntimeError(f"Failed to communicate with Tiger AI Gateway: {err}")

import requests
import urllib3
from src.config import TIGER_AI_GATEWAY_URL, TIGER_AI_GATEWAY_API_KEY, TIGER_AI_GATEWAY_MODEL

# Suppress insecure connection warnings in the console when verify=False is active
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TigerGatewayClient:
    """A client to communicate directly with the Tiger AI Gateway using HTTP requests."""

    def __init__(self):
        # Format endpoint to OpenAI Chat Completions standard
        self.api_url = f"{TIGER_AI_GATEWAY_URL.rstrip('/')}/v1/chat/completions"
        self.api_key = TIGER_AI_GATEWAY_API_KEY
        self.model = TIGER_AI_GATEWAY_MODEL

    def generate_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
        """Sends a request to the LLM gateway and returns the text response."""
        if not self.api_key:
            raise ValueError("TIGER_AI_GATEWAY_API_KEY is not defined in your environment (.env file).")
        if not self.model:
            raise ValueError("TIGER_AI_GATEWAY_MODEL is not defined in your environment (.env file).")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Build payload with system parameters and chat history context
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }

        try:
            # Added verify=False to bypass corporate SSL certificate decryption issues
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30,
                verify=False
            )
            response.raise_for_status()

            # Extract content from the OpenAI-style response JSON structure
            response_data = response.json()

            # ✅ FIXED: Added [0] index because choices is returned as a list
            return response_data["choices"][0]["message"]["content"].strip()

        except requests.exceptions.HTTPError as http_err:
            raise RuntimeError(f"Tiger AI Gateway HTTP Error: {http_err} - Details: {response.text}")
        except Exception as err:
            raise RuntimeError(f"Failed to communicate with Tiger AI Gateway: {err}")