"""
Calculator Tool

Provides deterministic arithmetic calculations for the Agent Gateway.
"""

from typing import Literal
from langchain_core.tools import tool


@tool
def calculate(a: float, b: float, operation: Literal["add", "subtract", "multiply", "divide"]) -> str:
    """
    Performs basic arithmetic operations between two numbers (a and b).
    Use this tool whenever you need to add, subtract, multiply, or divide numbers, loan balances, or limits.
    
    Args:
        a: The first number.
        b: The second number.
        operation: The operation to perform ('add', 'subtract', 'multiply', 'divide').
    """
    print(f"[DEBUG][TOOL: calculate] Computing: {a} {operation} {b}")
    op = operation.lower().strip()
    if op in ["add", "+"]:
        res = f"{a + b:,.2f}"
    elif op in ["subtract", "-"]:
        res = f"{a - b:,.2f}"
    elif op in ["multiply", "*"]:
        res = f"{a * b:,.2f}"
    elif op in ["divide", "/"]:
        if b == 0:
            res = "Error: Division by zero is undefined."
        else:
            res = f"{a / b:,.2f}"
    else:
        res = f"Error: Unsupported operation '{operation}'. Supported operations are add, subtract, multiply, divide."
        
    print(f"[DEBUG][TOOL: calculate] Result: {res}")
    return res
