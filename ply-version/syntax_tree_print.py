from syntax_tree import *

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
            elif isinstance(node, Klass):
                result = "Klass: "
                if node.name:
                    result += node.name
                if node.base:
                    result += " extends " + node.base.name
                print(result)
                for name, kind in node.vars.items():
                    print(self.indent + '  ', end='')
                    print('VarDecl: ' + name + ' ' + str(kind))
            elif self.expr_details and isinstance(node, Expr):
                print(node.node_type() + ' <' + str(node.kind) + '>', end=': ')
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
        return node

    def leave(self, node):
        if self.current_ignore == node:
            self.current_ignore = None
            self.ignore.remove(node)
        self.level -= 1
        self.indent = self.indent[:-2]
        return node
