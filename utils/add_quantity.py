from sympy import expand, sympify  # type: ignore
from typing import cast, Dict
from sympy import Expr
import re

class AddQuantity:
    def __init__(self):
        # Dictionary to map variable names to their original identifiers
        self.variable_map: Dict[str, str] = {}

    #Example ckeabed formula: (2022-P1Berekeningopzetkast1323-KLEUR.xlsx_OVERZICHTCOZ1323_G31*2022-P1Berekeningopzetkast1323-KLEUR.xlsx_OVERZICHTCOZ1323_C33)+('calculatiecat2022.xlsx_c.basis_I59*3.5)
    #Expected output: 
    #   Reference_1*Reference_2+Reference_3*3.5
    #   Dict 
    #   {
    #       Reference_1: 2022-P1Berekeningopzetkast1323-KLEUR.xlsx_OVERZICHTCOZ1323_G31
    #       Reference_2: 2022-P1Berekeningopzetkast1323-KLEUR.xlsx_OVERZICHTCOZ1323_C33
    #       Reference_3: calculatiecat2022.xlsx_c.basis_I59
    #   }

    def clean_formula(self, formula: str) -> str:
        formula = formula.replace("'", "")
        return formula

    def convert_to_expr(self, formula: str) -> Expr:
        # Updated pattern to match Excel file references with special characters

        pattern = r"([\w\-\.]+)_([\w\-\.]+)_([\w\-\.]+)"
        
        # Function to replace each match with a formatted variable name
        def replace_match(match: re.Match[str]) -> str:
            # Create a safe variable name by replacing special characters
            safe_name = f"ref_{len(self.variable_map)}"
            # Store the mapping of safe name to original identifier
            self.variable_map[safe_name] = match.group(0)
            return safe_name

        # Replace Excel-style references with safe variable names
        processed_formula = re.sub(pattern, replace_match, formula)
        
        try:
            # Convert the processed formula string to a SymPy expression
            return cast(Expr, sympify(processed_formula))
        except Exception as e:
            raise ValueError(f"Failed to parse formula: {formula}. Error: {str(e)}")

    def simpy_formula(self, formula: str) -> Expr:
        # Expand the SymPy expression to simplify it
        formula = self.clean_formula(formula)
        expr = self.convert_to_expr(formula)
        return cast(Expr, expand(expr))

    def get_original_identifier(self, variable_name: str) -> str:
        # Retrieve the original identifier from the variable name
        return self.variable_map.get(variable_name, "Unknown identifier")




