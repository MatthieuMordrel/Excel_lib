from pathlib import Path
import json
import os
from typing import List, Dict
import logging
from collections import defaultdict

class ResultManager:
    """Handles loading, saving, and managing results."""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self.summary_logger = SummaryLogger()
        self.formula_summarizer = FormulaSummarizer()
        
    def load_existing_results(self) -> list:
        """Loads existing results from the log file."""
        if not os.path.exists(self.log_path):
            return []
            
        try:
            with open(self.log_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    def save_results(self, results: List[Dict]):
        """Save results with classification tracking"""
        with open(self.log_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        # Update both summaries
        for result in results:
            self.summary_logger.classify_result(result)
            self.formula_summarizer.process_result(result)
        
        # Save both logs
        self.formula_summarizer.save_formula_summary()

class SummaryLogger:
    """Tracks and logs classification summary"""
    def __init__(self):
        self.counts = {
            'products': 0,
            'elements': 0,
            'base_materials': 0,
            'other': 0
        }
    
    def classify_result(self, result: Dict):
        """Categorize individual results"""
        if result.get('isProduct'):
            self.counts['products'] += 1
        elif result.get('isElement'):
            self.counts['elements'] += 1
        elif result.get('isBaseMaterial'):
            self.counts['base_materials'] += 1
        else:
            self.counts['other'] += 1
    

class FormulaSummarizer:
    """Groups formulas by type and usage patterns"""
    def __init__(self):
        self.formula_data = {
            'products': defaultdict(lambda: {'count': 0, 'unique_ids': set()}),
            'elements': defaultdict(lambda: {'count': 0, 'unique_ids': set()}),
            'base_materials': defaultdict(lambda: {'count': 0, 'unique_ids': set()}),
            'other': defaultdict(lambda: {'count': 0, 'unique_ids': set()})
        }
        self.processed_ids = set()  # Track already processed IDs

    def process_result(self, result: Dict):
        """Entry point for processing results and their nested references"""
        self._process_result_recursive(result)

    def _process_result_recursive(self, result: Dict):
        """Recursively processes result and its references"""
        # Skip results without ID or already processed
        if 'id' not in result or result['id'] in self.processed_ids:
            return
        
        self.processed_ids.add(result['id'])
        
        # Only process results with actual formulas
        if 'cleaned_formula' in result:
            self._categorize_formula(result)
        
        # Process nested references that have IDs
        for ref in result.get('references', []):
            if 'id' in ref:  # Only process references with IDs
                self._process_result_recursive(ref)

    def _categorize_formula(self, result: Dict):
        """Handles formula categorization for a single result"""
        # Require both ID and formula to categorize
        if 'id' not in result or 'cleaned_formula' not in result:
            return
            
        formula = result['cleaned_formula']
        category = 'other'
        
        if result.get('isProduct'):
            category = 'products'
        elif result.get('isElement'):
            category = 'elements'
        elif result.get('isBaseMaterial'):
            category = 'base_materials'

        # Update counts and IDs
        self.formula_data[category][formula]['count'] += 1
        self.formula_data[category][formula]['unique_ids'].add(result['id'])
    
    def save_formula_summary(self):
        """Save formatted summary to JSON file, overwriting previous"""
        output = {}
        
        for category, formulas in self.formula_data.items():
            output[category] = []
            for formula, data in formulas.items():
                output[category].append({
                    'cleaned_formula': formula,
                    'count': data['count'],
                    'unique_ids': list(data['unique_ids'])
                })
        
        # Write to temporary file first to ensure atomic write
        temp_path = Path('Logs/formula_summary.tmp')
        with open(temp_path, 'w') as f:
            json.dump(output, f, indent=2)
        
        # Replace old file atomically
        final_path = Path('Logs/formula_summary.json')
        temp_path.replace(final_path) 