"""
Service for extracting card metadata using OpenAI Vision API
"""
import base64
import json
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path
from openai import OpenAI, APIError, APITimeoutError
from app.core.config import settings

logger = logging.getLogger(__name__)


class VisionService:
    """Service for analyzing card images with GPT-4 Vision"""

    # System prompt for card metadata extraction
    SYSTEM_PROMPT = """You are a sports card identification expert. Analyze the provided card image and extract all visible metadata.

Focus on:
- Player name (exactly as printed on card)
- Year (card release year, not player's birth year)
- Brand/Manufacturer (Topps, Panini, Upper Deck, etc.)
- Card number (exactly as printed, including prefixes/suffixes)
- Set name (the specific set/series this card belongs to)
- Sport (Baseball, Basketball, Football, Hockey, Soccer, etc.)
- Condition (only if clearly visible damage/wear: Mint, Near Mint, Excellent, Good, Fair, Poor)

Return ONLY valid JSON with this exact structure:
{
  "player_name": "string or null",
  "year": integer or null,
  "brand": "string or null",
  "card_number": "string or null",
  "set_name": "string or null",
  "sport": "string or null",
  "condition": "string or null",
  "confidence": "high" | "medium" | "low",
  "notes": "any relevant observations"
}

Rules:
- Use null for fields you cannot determine with confidence
- For year, only return the card year if clearly visible (not estimated)
- For condition, only assess if clear signs of wear/damage are visible
- Be conservative: if unsure, use null
- confidence: "high" if most fields identified, "medium" if some fields, "low" if only 1-2 fields
"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Vision Service

        Args:
            api_key: OpenAI API key (defaults to settings)
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        if not self.api_key:
            logger.warning("OpenAI API key not configured - vision service will not work")
            self.client = None
        else:
            self.client = OpenAI(
                api_key=self.api_key,
                timeout=settings.VISION_TIMEOUT
            )

    def is_available(self) -> bool:
        """Check if vision service is available (API key configured)"""
        return self.client is not None

    async def extract_card_metadata(
        self,
        image_path: str
    ) -> Tuple[Optional[Dict], Optional[str], Optional[str]]:
        """
        Extract card metadata from image using GPT-4 Vision

        Args:
            image_path: Absolute path to saved card image

        Returns:
            Tuple of (metadata_dict, confidence_level, error_message)
            - metadata_dict: Extracted fields or None on failure
            - confidence_level: "high", "medium", "low", or None
            - error_message: Error description or None on success
        """
        if not self.is_available():
            logger.error("Vision service not available - missing API key")
            return None, None, "Vision service not configured"

        try:
            # Read and encode image
            image_base64 = self._encode_image(image_path)

            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model=settings.VISION_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this sports card and extract all visible metadata."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": settings.VISION_DETAIL_LEVEL
                                }
                            }
                        ]
                    }
                ],
                max_tokens=settings.VISION_MAX_TOKENS,
                response_format={"type": "json_object"}
            )

            # Parse response
            content = response.choices[0].message.content
            metadata = self._parse_vision_response(content)

            if metadata:
                confidence = metadata.pop("confidence", "medium")
                notes = metadata.pop("notes", None)

                # Log extraction
                logger.info(
                    f"Vision API extracted metadata with {confidence} confidence: "
                    f"{metadata.get('player_name', 'Unknown')}"
                )

                return metadata, confidence, None
            else:
                return None, None, "Failed to parse Vision API response"

        except APITimeoutError:
            logger.error("Vision API timeout")
            return None, None, "Vision API request timed out"

        except APIError as e:
            logger.error(f"Vision API error: {str(e)}")
            return None, None, f"Vision API error: {str(e)}"

        except Exception as e:
            logger.exception(f"Unexpected error in vision service: {str(e)}")
            return None, None, f"Unexpected error: {str(e)}"

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def _parse_vision_response(self, content: str) -> Optional[Dict]:
        """
        Parse JSON response from Vision API

        Args:
            content: Raw JSON string from API

        Returns:
            Parsed metadata dict or None if parsing fails
        """
        try:
            data = json.loads(content)

            # Validate expected fields exist
            if not isinstance(data, dict):
                logger.error("Vision API returned non-dict response")
                return None

            # Clean up the data - remove empty strings, convert to None
            cleaned = {}
            for key, value in data.items():
                if value == "" or value == "null" or value == "unknown":
                    cleaned[key] = None
                elif key == "year" and value is not None:
                    # Ensure year is int
                    try:
                        cleaned[key] = int(value)
                    except (ValueError, TypeError):
                        cleaned[key] = None
                else:
                    cleaned[key] = value

            return cleaned

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Vision API JSON: {str(e)}")
            return None
