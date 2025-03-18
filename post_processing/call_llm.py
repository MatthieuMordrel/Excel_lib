import json
import sys
from pathlib import Path
import logging
import concurrent.futures
from typing import List, Dict, Any
sys.path.append(str(Path(__file__).parent.parent))
from dotenv import load_dotenv # type: ignore
from openai import OpenAI
from schema.schema import LLMProcessedProduct
import os

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

PROMPT = open('post_processing/Prompts/prompt_price_hardcoded_BM.txt', 'r').read()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

def process_product(product: LLMProcessedProduct) -> tuple[LLMProcessedProduct | None, bool]:
    """
    Process a single product object with the LLM
    Returns a tuple of (processed_product, is_error)
    """
    product_id = product.get('id', 'unknown')
    try:
        logging.info(f"Processing product {product_id}")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PROMPT},
                {"role": "user", "content": json.dumps(product)}
            ],
            temperature=0.1
        )
        
        if not response.choices[0].message.content:
            logging.warning(f"Empty response for product {product_id}")
            # Save failed product to error log
            with open('llm_error_log.json', 'a') as f:
                json.dump({'product_id': product_id, 'error': 'Empty response'}, f)
                f.write('\n')
            return None, True
            
        raw_response = response.choices[0].message.content
        logging.debug(f"Raw response for product {product_id}: {raw_response}")
        
        try:
            result = json.loads(raw_response)
            logging.info(f"Successfully processed product {product_id}")
            return result, False
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON response for product {product_id}: {str(e)}")
            logging.debug(f"Raw response content: {raw_response}")
            # Save failed product to error log
            with open('llm_error_log.json', 'a') as f:
                json.dump({'product_id': product_id, 'error': str(e), 'raw_response': raw_response}, f)
                f.write('\n')
            return None, True
            
    except Exception as e:
        logging.error(f"Error processing product {product_id}: {str(e)}")
        # Save failed product to error log
        with open('llm_error_log.json', 'a') as f:
            json.dump({'product_id': product_id, 'error': str(e)}, f)
            f.write('\n')
        return None, True

def process_products_parallel(products: List[LLMProcessedProduct], max_workers: int = 5) -> tuple[List[LLMProcessedProduct], List[Dict[str, Any]]]:
    """
    Process products in parallel using ThreadPoolExecutor
    Returns a tuple of (processed_products, error_logs)
    """
    processed_products: List[LLMProcessedProduct] = []
    error_logs: List[Dict[str, Any]] = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_product = {
            executor.submit(process_product, product): product
            for product in products
        }
        
        for future in concurrent.futures.as_completed(future_to_product):
            product = future_to_product[future]
            try:
                result, is_error = future.result()
                if result:
                    processed_products.append(result)
                if is_error:
                    error_logs.append({
                        'product_id': product.get('id', 'unknown'),
                        'product_data': product
                    })
            except Exception as e:
                logging.error(f"Error processing product {product.get('id', 'unknown')}: {str(e)}")
                error_logs.append({
                    'product_id': product.get('id', 'unknown'),
                    'product_data': product,
                    'error': str(e)
                })
    
    return processed_products, error_logs

def process_log_file(input_path: str, output_path: str, test_mode: bool = False):
    """
    Process the entire log file and save results incrementally
    """
    logging.info(f"Starting processing of file: {input_path}")
    
    try:
        with open(input_path, 'r') as f:
            products = json.load(f)
        
        if test_mode:
            products = products[:1]
        
        processed_products, error_logs = process_products_parallel(products)
        
        # Save successful results
        with open(output_path, 'w') as f:
            json.dump(processed_products, f, indent=2)
        
        # Save error logs if any
        if error_logs:
            error_path = output_path.replace('.json', '_errors.json')
            with open(error_path, 'w') as f:
                json.dump(error_logs, f, indent=2)
            logging.info(f"Saved {len(error_logs)} error logs to: {error_path}")
        
        logging.info(f"Processing complete. Saved {len(processed_products)} products to: {output_path}")
    
    except Exception as e:
        logging.error(f"Error during file processing: {str(e)}")
        raise

# Example usage
if __name__ == "__main__":
    # Normal mode
    # process_log_file('simplified_log.json', 'processed_log.json')
    path = 'Logs/Current Logs/no_formula_log.json'
    process_log_file(path, 
                     path.replace('no_formula_log.json', 'processed_log.json'), 
                     test_mode=False)
