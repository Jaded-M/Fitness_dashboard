from __future__ import annotations

import json
import os
import requests

from dotenv import load_dotenv


def search_food_gemini(query: str) -> dict | None:
    if not query or not query.strip():
        return None

    query = query.strip()

        # Step 1: Search Open Food Facts API
    try:
        url = "https://world.openfoodfacts.org/cgi/search.pl"
        params = {
            "search_terms": query,
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 1
        }
        headers = {
            "User-Agent": "FitnessDashboard/1.0"
        }
        # Fail safe: Set a tighter timeout so the UI doesn't hang
        response = requests.get(url, params=params, headers=headers, timeout=3)
        response.raise_for_status()
        data = response.json()
        
        products = data.get("products", [])
        # Fail safe: Ensure products is a list and has at least one item
        if products and isinstance(products, list) and len(products) > 0:
            product = products[0]
            nutriments = product.get("nutriments", {})
            
            # Fail safe: Ensure nutriments exists before returning
            if nutriments:
                return {
                    "calories": nutriments.get("energy-kcal_100g", 0) or 0,
                    "protein_g": nutriments.get("proteins_100g", 0) or 0,
                    "carbs_g": nutriments.get("carbohydrates_100g", 0) or 0,
                    "fat_g": nutriments.get("fat_100g", 0) or 0,
                    "serving_size": product.get("serving_size", "100g") or "100g"
                }
    except Exception as e:
        print(f"Open Food Facts search error: {e}")
        # Proceed to Gemini fallback on any error

    # Step 2: Fall back to Gemini
    try:
        import google.generativeai as genai

        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("No GEMINI_API_KEY found.")
            return None

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")
        prompt = (
            "Return ONLY a JSON object with these exact keys for "
            f"{query}: calories, protein_g, carbs_g, fat_g, serving_size. "
            "No explanation, no markdown, just raw JSON. Use numbers for macros."
        )
        # Prevent Gemini SDK from retrying endlessly on quota errors (429)
        response = model.generate_content(prompt, request_options={"timeout": 5})
        text = response.text.strip()
        
        # Fail safe: Clean up markdown formatting if Gemini includes it
        text = text.removeprefix("```json").removesuffix("```").strip()
        text = text.removeprefix("```").removesuffix("```").strip()
        
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"JSON parsing error from Gemini: {e}")
        return None
    except Exception as e:
        print(f"Gemini error: {e}")
        return None
