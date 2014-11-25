#!/usr/bin/python3
from lexer import lexer
from parser import parser
from syntax_tree import *
from utils import for_each_file_do

class PrintVisitor(NodeVisitor):
    def __init__(self, expr_details=True):
        self.expr_details = expr_details
        self.level = 0
        self.indent = ''
        self.ignore = set()
        self.current_ignore = None

    def enter(self, node):
        if node in self.ignore:
            self.current_ignore = node
        if not self.current_ignore:
            print(self.indent, end='')
            if isinstance(node, FuncDecl):
                print(node, end=' => ')
                print(node.ret)
            elif self.expr_details and isinstance(node, (Expr, SimpleStat)):
                print(node.node_type(), end=': ')
                print(node)
            elif self.expr_details and isinstance(node, SimpleStat):
                print(node.node_type(), end=': ')
                print(node)
            else:
                print(node)
            if not self.expr_details:
                if isinstance(node, (Stat, IfBranch)):
                    if hasattr(node, 'expr'):
                        self.ignore.add(node.expr)
                    if hasattr(node, 'lhs'):
                        self.ignore.add(node.lhs)
                    if hasattr(node, 'rhs'):
                        self.ignore.add(node.rhs)
        self.level += 1
        self.indent += '  '
        if isinstance(node, FuncDecl):
            node.args.visit(self)

    def leave(self, node):
        if self.current_ignore == node:
            self.current_ignore = None
            self.ignore.remove(node)
        self.level -= 1
        self.indent = self.indent[:-2]

def process(content, filename):
    prog = parser.parse(content)
    if prog:
        prog.visit(PrintVisitor())

if __name__ == '__main__':
    for_each_file_do(process)
