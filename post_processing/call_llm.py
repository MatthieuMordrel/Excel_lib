import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from dotenv import load_dotenv # type: ignore
from openai import OpenAI
from schema.schema import LLMProcessedProduct
import os

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

PROMPT = open('post_processing/file.txt', 'r').read()

def process_product(product: LLMProcessedProduct) -> LLMProcessedProduct | None:
    """
    Process a single product object with the LLM
    """
    try:
        response = client.chat.completions.create(
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
    path = 'Logs/Previous Logs/Local + Elements/simplified_log.json'
    process_log_file(path, 
                     path.replace('simplified_log.json', 'processed_log.json'), 
                     test_mode=True)
