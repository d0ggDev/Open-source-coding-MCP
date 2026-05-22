from typing import Dict, Any, Union, Callable

# Define the Calculator class
class Calculator:
    """
    A simple calculator API that supports addition, subtraction, multiplication, and division.
    """
    def __init__(self):
        """
        Initialize the Calculator.
        """
        self.operations: Dict[str, Callable[[Any, Any], Any]] = {
            'add': lambda x, y: x + y,
            'subtract': lambda x, y: x - y,
            'multiply': lambda x, y: x * y,
            'divide': lambda x, y: x / y if y != 0 else None
        }

    def calculate(self, operation: str, a: Any, b: Any) -> Union[Any, None]:
        """
        Perform a calculation based on the specified operation.

        :param operation: The operation to perform (add, subtract, multiply, divide).
        :param a: The first operand.
        :param b: The second operand.
        :return: The result of the calculation or None if division by zero occurs.
        """
        try:
            if operation in self.operations:
                return self.operations[operation](a, b)
            else:
                raise ValueError("Invalid operation")
        except ValueError as e:
            print(f"Error: {e}")
            return None

# Test the Calculator
if __name__ == "__main__":
    calc = Calculator()
    
    # Test cases
    assert calc.calculate('add', 5, 3) == 8
    assert calc.calculate('subtract', 10, 4) == 6
    assert calc.calculate('multiply', 6, 7) == 42
    assert calc.calculate('divide', 10, 2) == 5
    
    # Test edge cases
    assert calc.calculate('divide', 10, 0) is None
    assert calc.calculate('invalid', 5, 3) is None
    
    print("All tests passed!")
