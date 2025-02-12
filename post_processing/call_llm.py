import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from dotenv import load_dotenv # type: ignore
import openai
from schema.schema import LLMProcessedProduct
import os

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

PROMPT = """You are an AI assistant tasked with extracting relationships from a product to build a structured database. You will receive a JSON object representing a product and must generate a new JSON object that details its relationships.

A product can be composed of other products, elements, or base materials. Your objective is to analyze the provided formula, determine how each referenced component contributes to the product, and update the quantities accordingly.

Example:
Input:
json
Copy
Edit
{
  "type": "product",
  "file": "2022 - P1 Berekening  Ladenkasten 794-KLEUR.xlsx",
  "sheet": "OVERZICHT COP",
  "cell": "D65",
  "cleaned_formula": "'CO30'!H59+4*('LADE 30'!H37+FR296x196!H33)",
  "id": "CO4L30_1",
  "references": [
    {
      "type": "element",
      "id": "CO30_47.577"
    },
    {
      "type": "element",
      "id": "LADE 30_18.65"
    },
    {
      "type": "element",
      "id": "FR296x196_3.445"
    }
  ]
}
Expected Output:
json
Copy
Edit
{
  "type": "product",
  "file": "2022 - P1 Berekening  Ladenkasten 794-KLEUR.xlsx",
  "sheet": "OVERZICHT COP",
  "cell": "D65",
  "cleaned_formula": "'CO30'!H59+4*('LADE 30'!H37+FR296x196!H33)",
  "id": "CO4L30_1",
  "quantity": 1,
  "references": [
    {
      "type": "element",
      "id": "CO30_47.577",
      "quantity": 1
    },
    {
      "type": "element",
      "id": "LADE 30_18.65",
      "quantity": 4
    },
    {
      "type": "element",
      "id": "FR296x196_3.445",
      "quantity": 4
    }
  ]
}
Your role is to process the cleaned_formula field to determine the correct quantity of each referenced component and update the JSON object accordingly."""  # Your full prompt here

def process_product(product: LLMProcessedProduct) -> LLMProcessedProduct | None:
    """
    Process a single product object with the LLM
    """
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": json.dumps(product)}
            ],
            temperature=0.1  # Keep low for consistent results
        )
        return json.loads(response.choices[0].message.content or "{}")  # Provide fallback empty JSON
    except Exception as e:
        print(f"Error processing product {product.get('id')}: {str(e)}")
        return None  # Return None instead of {}

def process_log_file(input_path: str, output_path: str, test_mode: bool = False):
    """
    Process the entire log file and save results
    """
    with open(input_path, 'r') as f:
        products = json.load(f)
    
    processed_products = []
    for product in products:
        result = process_product(product)
        if result:
            processed_products.append(result)  # type: ignore
        if test_mode:  # Stop after first product in test mode
            break
    
    with open(output_path, 'w') as f:
        json.dump(processed_products, f, indent=2)

# Example usage
if __name__ == "__main__":
    # Normal mode
    # process_log_file('simplified_log.json', 'processed_log.json')
    
    # Test mode
    process_log_file('Logs/Previous Logs/Multipled Element + Elements/simplified_log.json', 'Logs/Previous Logs/Multipled Element + Elements/processed_log.json', test_mode=False)
