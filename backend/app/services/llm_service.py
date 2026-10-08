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

    def get_fallback_response(self, structured_context: PredictionResponse, user_message: str = "") -> str:
        """
        Deterministic fallback if LLM is unavailable or fails.
        """
        if not self.is_enabled or not self.api_key:
            base_msg = "Conversational AI is not configured. Please configure GEMINI_API_KEY. "
        else:
            base_msg = "I'm currently unable to process natural language generation. "
            
        from app.services.medical_info_service import medical_info_service
        lower_msg = user_message.lower()
        matched_condition = None
        for condition in medical_info_service._recommendations.keys():
            if condition.lower() in lower_msg:
                matched_condition = condition
                break

        if matched_condition:
            recs = medical_info_service.get_recommendations(matched_condition)
            base_msg += f"\n\nHere is some general self-care guidance for {matched_condition}:\n"
            for tip in recs.get("recommended_tips", []):
                base_msg += f"- {tip}\n"
            base_msg += "\nWhen to seek medical care:\n"
            for tip in recs.get("when_to_seek_care", []):
                base_msg += f"- {tip}\n"
        else:
            if structured_context and structured_context.predictions:
                base_msg += "Based on the symptoms provided, the system identified preliminary information. "
                
                if structured_context.urgency and structured_context.urgency.level == "urgent_attention":
                    base_msg += "IMPORTANT: " + structured_context.urgency.message + " "
                    
                if structured_context.specialist_recommendation:
                    base_msg += f"A {structured_context.specialist_recommendation.specialist} may be an appropriate starting point. "
                
        base_msg += "\n\nPlease note that this information is not a medical diagnosis."
        return base_msg

    def generate_response(self, user_message: str, structured_context: PredictionResponse, conversation_history: list = None, patient_context: str = "") -> str:
        """
        Generates a conversational response strictly summarizing the backend structured context and relevant history.
        """
        if not self.client:
            return self.get_fallback_response(structured_context, user_message)
            
        try:
            # We dump the structured_context to a JSON string, excluding raw input dict to save tokens
            context_dict = structured_context.model_dump(exclude={'input', 'success'})
            context_json = json.dumps(context_dict, indent=2)
            
            prompt = f"{MEDICAL_ASSISTANT_SYSTEM_PROMPT}\n\nCURRENT SYMPTOM ANALYSIS CONTEXT:\n```json\n{context_json}\n```\n\n"
            
            if patient_context:
                prompt += f"RELEVANT PATIENT HISTORY:\n{patient_context}\n\n"
                
            if conversation_history:
                prompt += "PREVIOUS CONVERSATION HISTORY:\n"
                for msg in conversation_history:
                    prompt += f"{msg['role'].upper()}: {msg['content']}\n\n"
                    
            prompt += f"USER MESSAGE:\n{user_message}"
            
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
                
            return self.get_fallback_response(structured_context, user_message)
            
        except Exception as e:
            print(f"Gemini API generation error: {e}")
            return self.get_fallback_response(structured_context, user_message)

    def get_image_observations(self, image_bytes: bytes, mime_type: str) -> str:
        """
        Extracts safe, non-diagnostic visual observations from an image.
        """
        if not self.client:
            return "Vision AI is currently disabled or unconfigured."
            
        prompt = (
            "You are an academic medical vision assistant. "
            "Please describe only the visible, non-diagnostic observations from this image. "
            "Clearly identify uncertainty and image-quality limitations. "
            "CRITICAL RULES: \n"
            "- Avoid claiming to identify a disease, infection, cancer, or other medical condition.\n"
            "- Never prescribe medication or treatment.\n"
            "- Never independently determine emergency urgency.\n"
            "- Describe visual characteristics like redness, swelling, texture, color, and location, but do NOT give a diagnosis."
        )
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    genai.types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                    prompt
                ],
                config=genai.types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=300,
                )
            )
            
            if response and response.text:
                return response.text.strip()
            return "Unable to generate observations for this image."
        except Exception as e:
            print(f"Gemini API vision error: {e}")
            return "Error processing image observations."

    def get_report_summary(self, text_or_bytes, is_image: bool = False, mime_type: str = "") -> str:
        """
        Summarizes a medical report (either extracted text or an image of a report).
        """
        if not self.client:
            return "AI Summarization is currently disabled or unconfigured."
            
        prompt = (
            "You are a medical AI assistant tasked with summarizing a medical report for a patient.\n"
            "CRITICAL RULES:\n"
            "- Use ONLY information present in the report.\n"
            "- Preserve original values, units, reference ranges, and dates exactly.\n"
            "- Flag any ambiguous or illegible values.\n"
            "- NEVER invent values or interpret missing reference ranges as normal.\n"
            "- DO NOT diagnose, prescribe, recommend medication changes, declare the user healthy, or claim to rule out disease.\n"
            "- Clearly state that reference ranges vary and this summary may contain errors, encouraging review with a qualified healthcare professional."
        )
        
        try:
            if is_image:
                contents = [
                    genai.types.Part.from_bytes(data=text_or_bytes, mime_type=mime_type),
                    prompt
                ]
            else:
                contents = [
                    f"MEDICAL REPORT TEXT:\n{text_or_bytes}\n\n",
                    prompt
                ]
                
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=genai.types.GenerateContentConfig(
                    temperature=0.1,
                    max_output_tokens=1000,
                )
            )
            
            if response and response.text:
                return response.text.strip()
            return "Unable to generate summary for this report."
        except Exception as e:
            print(f"Gemini API summary error: {e}")
            return "Error generating report summary."

llm_service = LLMService()
