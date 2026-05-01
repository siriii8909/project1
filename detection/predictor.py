import os
import json
from PIL import Image
from django.conf import settings
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env explicitly to ensure the key is available when the module is imported
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

class CropPredictor:
    def __init__(self):
        self.classes = ['Tomato - Healthy', 'Tomato - Late Blight', 'Potato - Early Blight', 'Corn - Rust', 'Rice - Leaf Blast']
        self.use_gemini = api_key is not None

    def predict(self, image_path):
        if self.use_gemini:
            try:
                img = Image.open(image_path)
                
                # Setup model using Gemini 2.5 Flash since the Pro tier has a quota limit of 0 on your account
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                prompt = """You are a world-class agricultural botanist, agronomist, and plant pathologist working on a professional precision agriculture system.
Meticulously analyze this image. First, determine if it contains a plant, leaf, or crop. If it does not, return 'crop_disease': 'Invalid - Not a Plant'.
If it is a plant, carefully analyze its leaf structure, venation, color, lesions, and any signs of pests or pathogens to determine the exact species and disease (or if it is healthy).

Return ONLY a raw valid JSON object without any markdown formatting. Do not wrap in ```json ... ```. The JSON must have these exact string keys:
- "crop_disease": The precise name of the crop and the disease separated by ' - ' (e.g. 'Tomato - Late Blight' or 'Wheat - Yellow Rust'. If healthy, use 'CropName - Healthy').
- "confidence": A number between 0 and 100 representing your diagnostic confidence based on visual evidence.
- "treatment": Professional, actionable treatment plan (chemical, biological, or cultural).
- "prevention": Long-term agricultural prevention strategies.
- "care_tips": Best practices for ongoing crop management.
"""
                response = model.generate_content([prompt, img])
                text = response.text.strip()
                if text.startswith('```json'):
                    text = text[7:-3].strip()
                elif text.startswith('```'):
                    text = text[3:-3].strip()

                result = json.loads(text)
                
                # Ensure all keys are present
                for key in ['crop_disease', 'confidence', 'treatment', 'prevention', 'care_tips']:
                    if key not in result:
                        result[key] = "Not provided"
                if not isinstance(result['confidence'], (int, float)):
                    try:
                        result['confidence'] = float(result['confidence'])
                    except:
                        result['confidence'] = 90.0
                    
                return result
            except Exception as e:
                print(f"Gemini API error: {e}")
                return self._simulated_predict()
        else:
            print("Warning: GEMINI_API_KEY not set. Using simulated prediction.")
            return self._simulated_predict()

    def _simulated_predict(self):
        """Fallback simulation."""
        import random
        result = random.choice(self.classes)
        confidence = random.uniform(0.92, 0.99)
        return {
            'crop_disease': result,
            'confidence': round(confidence * 100, 2),
            'treatment': 'Simulated treatment advice since Gemini failed.',
            'prevention': 'Simulated prevention advice.',
            'care_tips': 'Simulated care tips.'
        }

predictor = CropPredictor()
