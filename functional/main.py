from typing import Union, List, Any

class ASTNode:
    pass

class Number(ASTNode):
    def __init__(self, value: float):
        self.value = value

class Variable(ASTNode):
    def __init__(self, name: str):
        self.name = name

class Assignment(ASTNode):
    def __init__(self, name: str, value: ASTNode):
        self.name = name
        self.value = value

class BinaryOp(ASTNode):
    def __init__(self, left: ASTNode, operator: str, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right

class IfStatement(ASTNode):
    def __init__(self, condition: ASTNode, then_branch: ASTNode, else_branch: ASTNode = None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

def tokenize(input_code: str) -> List[str]:
    import re
    token_pattern = r"\s*(=>|[-+*/=><()])|([a-zA-Z_][a-zA-Z0-9_]*)|([0-9]+)"
    tokens = re.findall(token_pattern, input_code)
    return [t[0] or t[1] or t[2] for t in tokens]

def parse(tokens: List[str]):
    def parse_expression(pos: int):
        def parse_primary(pos: int):
            token = tokens[pos]
            if token.isdigit():
                return Number(float(token)), pos + 1
            elif token.isidentifier():
                return Variable(token), pos + 1
            elif token == '(':
                node, new_pos = parse_expression(pos + 1)
                if tokens[new_pos] != ')':
                    raise SyntaxError("Expected closing parenthesis")
                return node, new_pos + 1
            raise SyntaxError(f"Unexpected token: {token}")

        def parse_binary_op(pos: int, precedence=0):
            left, pos = parse_primary(pos)
            while pos < len(tokens):
                op = tokens[pos]
                op_precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '>': 3, '<': 3, '=': 0}.get(op, -1)
                if op_precedence < precedence:
                    break
                right, new_pos = parse_binary_op(pos + 1, op_precedence + 1)
                left = BinaryOp(left, op, right)
                pos = new_pos
            return left, pos

        return parse_binary_op(pos)

    def parse_statement(pos: int):
        token = tokens[pos]
        if token.isidentifier() and tokens[pos + 1] == '=':
            name = token
            value, new_pos = parse_expression(pos + 2)
            return Assignment(name, value), new_pos
        elif token == 'if':
            condition, new_pos = parse_expression(pos + 1)
            if tokens[new_pos] != 'then':
                raise SyntaxError("Expected 'then'")
            then_branch, new_pos = parse_statement(new_pos + 1)
            
            else_branch = None
            if tokens[new_pos] == 'else':
                else_branch, new_pos = parse_statement(new_pos + 1)

            return IfStatement(condition, then_branch, else_branch), new_pos
        else:
            return parse_expression(pos)

    ast, _ = parse_statement(0)
    return ast

def evaluate(node: ASTNode, env: dict) -> Any:
    if isinstance(node, Number):
        return node.value
    elif isinstance(node, Variable):
        if node.name not in env:
            raise NameError(f"Variable '{node.name}' is not defined")
        return env[node.name]
    elif isinstance(node, Assignment):
        value = evaluate(node.value, env)
        env[node.name] = value
        return value
    elif isinstance(node, BinaryOp):
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        if node.operator == '+':
            return left + right
        elif node.operator == '-':
            return left - right
        elif node.operator == '*':
            return left * right
        elif node.operator == '/':
            if right == 0:
                raise ZeroDivisionError("Division by zero")
            return left / right
        elif node.operator == '>':
            return left > right
        elif node.operator == '<':
            return left < right
        elif node.operator == '=':
            return left == right
        else:
            raise ValueError(f"Unknown operator: {node.operator}")
    elif isinstance(node, IfStatement):
        condition = evaluate(node.condition, env)
        if condition:
            return evaluate(node.then_branch, env)
        elif node.else_branch:
            return evaluate(node.else_branch, env)
        return None
    else:
        raise TypeError(f"Unknown AST node: {type(node)}")

if __name__ == "__main__":
    env = {} 
    while True:
        code = input(">>> ")
        tokens = tokenize(code)

        ast = parse(tokens)
        result = evaluate(ast, env)
        print(result)
