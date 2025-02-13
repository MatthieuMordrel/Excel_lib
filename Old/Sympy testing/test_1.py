from sympy import symbols, expand, simplify, Expr, Number #type: ignore
from typing import cast
import sympy as sp

def demonstrate_arithmetic_operations() -> None:
    """
    Demonstrates how SymPy handles combined arithmetic operations including
    multiplication, addition, and division with both symbols and numbers.
    """
    # Define symbolic variables
    x, y, z = symbols('x y z')  
    
    print("1. Basic Combined Operations")
    print("-" * 50)
    
    # Multiplication with addition
    expr1: Expr = 2*x + 3*y * (x + z)
    print(f"Original expression: {expr1}")
    expanded1: Expr = cast(Expr, expand(expr1))
    print(f"Expanded form: {expanded1}")
    
    print("\n2. Division Operations")
    print("-" * 50)
    
    # Division with multiplication and addition
    expr2: Expr = (x + y)/(2*z) + x*y
    print(f"Expression with division: {expr2}")
    
    # Combine fractions
    combined: Expr = sp.together(expr2)
    print(f"Combined fraction: {combined}")
    
    print("\n3. Complex Arithmetic")
    print("-" * 50)
    
    # More complex expression with all operations
    expr3: Expr = (2*x + y)/(z + 1) * (x - y) + z/(x + 2)
    print(f"Complex expression: {expr3}")
    
    # Simplify the expression
    simplified: Expr = cast(Expr, simplify(expr3))
    print(f"Simplified form: {simplified}")
    
    print("\n4. Practical Example")
    print("-" * 50)
    
    # Example: Cost calculation formula
    # (base_cost + material_cost) * quantity / bulk_discount
    base_cost, material_cost, quantity, bulk_discount = symbols('base_cost material_cost quantity bulk_discount')
    cost_formula: Expr = (base_cost + material_cost) * quantity / bulk_discount
    
    # Substitute some values
    result = cast(Number, cost_formula.subs([ 
        (base_cost, 10),
        (material_cost, 5),
        (quantity, 100),
        (bulk_discount, 2)
    ]))
    
    print(f"Cost formula: {cost_formula}")
    print(f"Calculated cost (with values): {result}")
    
    print("\n5. Working with Coefficients")
    print("-" * 50)
    
    # Expression with coefficients
    expr4: Expr = 3*x/2 + 4*y/3 - z/6
    print(f"Expression with fractions: {expr4}")
    
    # Convert to common denominator
    common_denom: Expr = sp.together(expr4)
    print(f"With common denominator: {common_denom}")

if __name__ == "__main__":
    demonstrate_arithmetic_operations()
