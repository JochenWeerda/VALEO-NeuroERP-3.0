"""Bounded arithmetic for Rohware preview formulas; never executes Python code."""
import ast
import math
import operator

MAX_FORMULA_LENGTH = 1024
MAX_NODES = 128
MAX_DEPTH = 32
_BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
           ast.Mod: operator.mod, ast.Pow: operator.pow}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCTIONS = {'abs': abs, 'min': min, 'max': max, 'round': round}


def _number(value: object) -> float:
    if type(value) not in (int, float):
        raise ValueError('numeric value required')
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('finite value required')
    return value


def evaluate_formula(formula: str, context: dict[str, float]) -> float | None:
    """Evaluate only bounded numeric arithmetic; invalid expressions return None."""
    try:
        if type(formula) is not str or len(formula) > MAX_FORMULA_LENGTH or type(context) is not dict:
            return None
        tree = ast.parse(formula, mode='eval')
        if sum(1 for _ in ast.walk(tree)) > MAX_NODES:
            return None
        values = {key: _number(value) for key, value in context.items() if type(key) is str}
        values['feuchte_abzug_prozent'] = _number(max(0.0, values.get('feuchte', 14.0) - 14.0))

        def visit(node, depth=1):
            if depth > MAX_DEPTH:
                raise ValueError('formula too deep')
            if isinstance(node, ast.Constant):
                return _number(node.value)
            if isinstance(node, ast.Name):
                return values[node.id]
            if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
                return _number(_UNARY[type(node.op)](visit(node.operand, depth + 1)))
            if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
                left, right = visit(node.left, depth + 1), visit(node.right, depth + 1)
                return _number(_BINARY[type(node.op)](left, right))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCTIONS and not node.keywords:
                name = node.func.id
                if name == 'round' and len(node.args) == 2:
                    arg = node.args[1]
                    sign = 1
                    if isinstance(arg, ast.UnaryOp) and type(arg.op) in (ast.UAdd, ast.USub):
                        sign = -1 if isinstance(arg.op, ast.USub) else 1
                        arg = arg.operand
                    if not isinstance(arg, ast.Constant) or type(arg.value) is not int or abs(arg.value) > 308:
                        raise ValueError('invalid precision')
                    return _number(round(visit(node.args[0], depth + 1), sign * arg.value))
                args = [visit(arg, depth + 1) for arg in node.args]
                return _number(_FUNCTIONS[name](*args))
            raise ValueError('unsupported expression')

        return visit(tree.body)
    except (ValueError, TypeError, ArithmeticError, SyntaxError, RecursionError, MemoryError, KeyError):
        return None
