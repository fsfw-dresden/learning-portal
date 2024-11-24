from dataclasses import dataclass
from typing import List
import json
import re

@dataclass
class VisionResponse:
    look_at_coordinates: List[int]
    instructions: List[str]
    
    @classmethod
    def from_claude_response(cls, response_text: str):
        # Extract JSON from the response using regex
        json_match = re.search(r'\{[^}]+\}', response_text)
        if not json_match:
            raise ValueError("No JSON found in response")
            
        json_data = json.loads(json_match.group())
        
        return cls(
            look_at_coordinates=json_data['look_at_coordinates'],
            instructions=json_data['instructions']
        )
