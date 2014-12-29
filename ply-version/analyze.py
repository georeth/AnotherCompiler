#!/usr/bin/python3
import ply.yacc as yacc

from lexer import tokens
from syntax_tree import *
from syntax_tree_print import *

class AnalyzeVisitor(NodeVisitor):
    def __init__(self):
        self.var_stack = []
        self.kind_stack = []
    
    def resolve_kind(self, name):
        kind = self.kind_stack[-1].get(name)
        if kind is None:
            print("Unknown typename {0}!".format(name))
            raise Exception()
        return kind
    
    def resolve_var(self, name):
        var = self.var_stack[-1].get(name)
        if var is None:
            print("Undefined variable {0}!".format(name))
            raise Exception()
        return var

    def enter(self, node):
        if isinstance(node, Program):
            self.var_stack.append({})
            self.kind_stack.append({
                'boolean': BoolKind.kind,
                'integer': IntKind.kind,
            })
            for name, decl in node.decls.items():
                if isinstance(decl, FuncDecl):
                    self.var_stack[-1][name] = decl
                elif isinstance(decl, KindDecl):
                    self.kind_stack[-1][name] = decl.kind
        elif isinstance(node, FuncDecl):
            self.var_stack.append(dict(self.var_stack[-1]))
            node.args.visit(self)
            if node.ret:
                node.ret.visit(self)
                if isinstance(node.ret, KindRef):
                    node.ret = node.ret.kind
                    node.kind.ret = node.ret
        elif isinstance(node, Impl):
            self.var_stack.append(dict(self.var_stack[-1]))
        elif isinstance(node, ArrayKind):
            if isinstance(node.kind, KindRef):
                node.kind = self.resolve_kind(node.kind.name)
            node.kind.visit(self)
        elif isinstance(node, Klass):
            self.var_stack.append(dict(self.var_stack[-1]))
            if node.base:
                node.base = self.resolve_kind(node.base.name)
                node.base.visit(self)
                for name, decl in node.base.decls.items():
                    if isinstance(decl, FuncDecl):
                        self.var_stack[-1][name] = decl
                    else:
                        decl.visit(self)
            for name, decl in node.decls.items():
                if isinstance(decl, FuncDecl):
                    self.var_stack[-1][name] = decl
                else:
                    decl.visit(self)
        elif isinstance(node, KindRef):
            node.kind = self.resolve_kind(node.name)
        elif isinstance(node, VarRef):
            node.var = self.resolve_var(node.name)
            node.kind = node.var.kind
        elif isinstance(node, VarDecl):
            node.kind.visit(self)

    def leave(self, node):
        if isinstance(node, Program):
            self.var_stack.pop()
            self.kind_stack.pop()
        elif isinstance(node, (Impl, Klass)):
            self.var_stack.pop()
        elif isinstance(node, FuncDecl):
            self.var_stack.pop()
        elif isinstance(node, VarDecl):
            if isinstance(node.kind, KindRef):
                node.kind = node.kind.kind
            self.var_stack[-1][node.name] = node
        elif isinstance(node, ArrayKind):
            if isinstance(node.kind, KindRef):
                node.kind = self.resolve_kind(node.kind.name)
        elif isinstance(node, Expr) and node.kind is None:
            if isinstance(node, DotExpr):
                node.kind = node.expr.kind.decls[node.member].kind
            elif isinstance(node, CallExpr):
                node.kind = node.expr.kind.ret
            elif isinstance(node, BracketExpr):
                node.kind = node.expr.kind.kind
                if isinstance(node.kind, KindRef):
                    node.kind = self.resolve_kind(node.kind.name)
