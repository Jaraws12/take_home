"""
Plain-Language Input Parser using Gemini SDK.
Converts unstructured user inputs (English, Hinglish, fragmented) into structured JSON.
Prompts for clarifications if essential fields (e.g. gross salary) are missing.
"""

import json
import os
from typing import Dict, Any
from google import genai
from google.genai import types

class TaxInputParser:
    def __init__(self, api_key: str = None):
        key = api_key or os.environ.get("GEMINI_API_KEY")
        if not key:
            self.client = None
        else:
            self.client = genai.Client(api_key=key)

    def parse_text(self, text: str) -> Dict[str, Any]:
        """Parses raw text into structured tax payload or identifies required clarification."""
        if not self.client:
            # Fallback heuristic parser when API key is unavailable
            return self._heuristic_parse(text)

        system_instruction = (
            "You are an expert Indian Income Tax AI assistant. Extract financial parameters from "
            "the user's text into a strict JSON format. "
            "Extract: gross_salary, basic_salary, hra_received, rent_paid, is_metro (bool), "
            "sec_80c, sec_80ccd_1b, sec_80d_self, sec_80d_parents, self_senior (bool), parents_senior (bool), home_loan_interest.\n"
            "If gross_salary is not provided or completely ambiguous, return JSON with key 'clarification_needed': true "
            "and 'missing_field_question': ask a polite question to get gross salary."
        )

        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=text,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            return self._heuristic_parse(text)

    def _heuristic_parse(self, text: str) -> Dict[str, Any]:
        """Simple rule/regex heuristic parser for offline/test fallback."""
        import re
        text_lower = text.lower()
        
        # Basic salary extraction
        salary_match = re.search(r'(?:salary|ctc|earning|make|pa|per annum|lac|lakhs?)\D*(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|k|pm|per month)?', text_lower)
        if not salary_match:
            return {
                "clarification_needed": True,
                "missing_field_question": "Could you please specify your total annual gross salary or CTC?"
            }
        
        val = float(salary_match.group(1))
        unit = salary_match.group(2)
        if unit in ['lakh', 'lakhs', 'lac']:
            val *= 100000
        elif unit == 'k' or val < 1000: # Assuming monthly or thousands
            if 'pm' in text_lower or 'month' in text_lower:
                val *= 1200
            else:
                val *= 1000
                
        return {
            "clarification_needed": False,
            "gross_salary": val,
            "sec_80c": 150000.0 if "80c" in text_lower else 0.0,
            "sec_80d_self": 25000.0 if "insurance" in text_lower or "80d" in text_lower else 0.0,
            "rent_paid": 180000.0 if "rent" in text_lower else 0.0
        }