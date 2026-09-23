import json
from google import genai
from app.config import settings
from app.prompts.medical_assistant_prompt import MEDICAL_ASSISTANT_SYSTEM_PROMPT
from app.schemas import PredictionResponse

class LLMService:
    def __init__(self):
        self.client = None
        self.model_name = settings.GEMINI_MODEL
        self.is_enabled = settings.LLM_ENABLED
        self.api_key = settings.GEMINI_API_KEY.strip()
        
        if self.is_enabled and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Failed to initialize Gemini client: {e}")
                self.client = None

    def get_fallback_response(self, structured_context: PredictionResponse) -> str:
        """
        Deterministic fallback if LLM is unavailable or fails.
        """
        if not self.is_enabled or not self.api_key:
            base_msg = "Conversational AI is not configured. Please configure GEMINI_API_KEY. "
        else:
            base_msg = "I'm currently unable to process natural language generation. "
            
        base_msg += "Based on the symptoms provided, the system identified preliminary information. "
        
        if structured_context.urgency and structured_context.urgency.level == "urgent_attention":
            base_msg += "IMPORTANT: " + structured_context.urgency.message + " "
            
        if structured_context.specialist_recommendation:
            base_msg += f"A {structured_context.specialist_recommendation.specialist} may be an appropriate starting point. "
            
        base_msg += "Please note that this information is not a medical diagnosis."
        return base_msg

    def generate_response(self, user_message: str, structured_context: PredictionResponse) -> str:
        """
        Generates a conversational response strictly summarizing the backend structured context.
        """
        if not self.client:
            return self.get_fallback_response(structured_context)
            
        try:
            # We dump the structured_context to a JSON string, excluding raw input dict to save tokens
            context_dict = structured_context.model_dump(exclude={'input', 'success'})
            context_json = json.dumps(context_dict, indent=2)
            
            prompt = f"{MEDICAL_ASSISTANT_SYSTEM_PROMPT}\n\nSTRUCTURED CONTEXT:\n```json\n{context_json}\n```\n\nUSER MESSAGE:\n{user_message}"
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=0.2, # Keep it deterministic and strict
                    max_output_tokens=500,
                )
            )
            
            if response and response.text:
                return response.text.strip()
                
            return self.get_fallback_response(structured_context)
            
        except Exception as e:
            print(f"Gemini API generation error: {e}")
            return self.get_fallback_response(structured_context)

llm_service = LLMService()
