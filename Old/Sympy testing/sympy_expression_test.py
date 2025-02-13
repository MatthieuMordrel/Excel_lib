from sympy import symbols, expand, factor, simplify, Symbol, Expr #type: ignore
import sympy as sp

def test_sympy_expressions() -> None:
    """
    Demonstrates key SymPy features for developing and manipulating mathematical expressions.
    """
    # Define symbolic variables
    x, y, z = symbols('x y z')  # type: ignore
    
    print("1. Basic Expression Creation and Manipulation")
    print("-" * 50)
    
    # Create a polynomial expression
    expr1: Expr = x**2 + 2*x*y + y**2
    print(f"Original expression: {expr1}")
    
    # Factor the expression
    factored: Expr = factor(expr1)
    print(f"Factored form: {factored}")  # Should show (x + y)**2
    
    print("\n2. Working with Complex Expressions")
    print("-" * 50)
    
    # Create a more complex expression
    expr2: Expr = (x + y)**3 - (x - y)**2
    print(f"Complex expression: {expr2}")
    
    # Expand the expression
    expanded: Expr = expand(expr2) #type: ignore
    print(f"Expanded form: {expanded}")
    
    # Simplify the expression
    simplified: Expr = simplify(expanded) #type: ignore
    print(f"Simplified form: {simplified}")
    
    print("\n3. Expression Substitution")
    print("-" * 50)
    
    # Create an expression with multiple variables
    expr3: Expr = x**2 + y*z
    print(f"Expression: {expr3}")
    
    # Substitute values
    result1: sp.Number = expr3.subs([(x, 2), (y, 3), (z, 4)]) #type: ignore
    print(f"After substitution (x=2, y=3, z=4): {result1}")
    
    # Substitute expressions
    result2: Expr = expr3.subs(x, y + 1) #type: ignore
    print(f"After substituting x with (y + 1): {result2}")

if __name__ == "__main__":
    test_sympy_expressions() 