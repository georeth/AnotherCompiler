#!/usr/bin/python3
import ply.yacc as yacc

from lexer import tokens
from syntax_tree import *
from syntax_tree_print import *

class OptimizingVisitor(NodeVisitor):
    def __init__(self):
        self.binary_calc = {
            '+': (lambda x, y: x + y),
            '-': (lambda x, y: x - y),
            '*': (lambda x, y: x * y),
            '/': (lambda x, y: x // y),
            '%': (lambda x, y: x % y),

            '==': (lambda x, y: x == y),
            '!=': (lambda x, y: x != y),
            '<': (lambda x, y: x < y),
            '<=': (lambda x, y: x < y),
            '>': (lambda x, y: x > y),
            '>=': (lambda x, y: x >= y),
        }

    def enter(self, node):
        return node

    def leave(self, node):
        if isinstance(node, UnaryExpr):
            if isinstance(node.expr, ConstantExpr):
                if node.op == '+':
                    return NumLiteral(node.expr.value)
                elif node.op == '-':
                    return NumLiteral(-node.expr.value)
                elif node.op == 'not':
                    return BoolLiteral(1 - node.expr.value)
        elif isinstance(node, BinaryExpr):
            if (isinstance(node.lhs.value, ConstantExpr) and
                isinstance(node.rhs.value, ConstantExpr)):
                calc = self.binary_calc.get(node.op)
                if calc is not None:
                    result = calc(node.lhs.value, node.rhs.value)
                    if isinstance(result, bool):
                        return BoolLiteral.yes if calc else BoolLiteral.no
                    elif isinstance(result, bool):
                        return NumLiteral(result)

        return node

def optimize(prog):
    prog = prog.visit(OptimizingVisitor())
    return prog
