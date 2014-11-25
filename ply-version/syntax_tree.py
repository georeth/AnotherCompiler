#!/usr/bin/python3

class NodeVisitor(object):
    def enter(self, node):
        pass
    def leave(self, node):
        pass

class Node(object):
    def node_type(self):
        return type(self).__name__
    def __str__(self):
        return self.node_type()

    def visit(self, visitor):
        visitor.enter(self)
        visitor.leave(self)

class Program(Node):
    def __init__(self, name, args, decls, impl):
        self.name = name
        self.args = args
        self.decls = decls
        self.impl = impl

    def __str__(self):
        return self.node_type() + ": " + self.name + " "

    def visit(self, visitor):
        visitor.enter(self)
        for name, decl in self.decls.items():
            decl.visit(visitor)
        self.impl.visit(visitor)
        visitor.leave(self)

class FuncDecl(Node):
    def __init__(self, name, args, ret, impl):
        self.name = name
        self.args = args
        self.ret = ret
        self.impl = impl

    def __str__(self):
        return self.node_type() + ": " + self.name

    def visit(self, visitor):
        visitor.enter(self)
        self.impl.visit(visitor)
        visitor.leave(self)

class ArgList(Node):
    def __init__(self, names, decls):
        self.names = names
        self.args = list(map(lambda name: decls[name], names))

    def __str__(self):
        return self.node_type() + ": " + ", ".join(self.names)

    def visit(self, visitor):
        visitor.enter(self)
        for decl in self.args:
            decl.visit(visitor)
        visitor.leave(self)

class Impl(Node):
    def __init__(self, vars, stats):
        self.vars = vars
        self.stats = stats

    def visit(self, visitor):
        visitor.enter(self)
        for name, decl in self.vars.items():
            decl.visit(visitor)
        for stat in self.stats:
            stat.visit(visitor)
        visitor.leave(self)

class VarDecl(Node):
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind

    def __str__(self):
        return self.node_type() + ": " + self.name + " " + str(self.kind)

class KindDecl(Node):
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind

    def __str__(self):
        return self.node_type() + ": " + self.name

    def visit(self, visitor):
        visitor.enter(self)
        self.kind.visit(visitor)
        visitor.leave(self)

class KindRef(Node):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "<" + self.name + ">"

class Kind(Node):
    pass

class NumKind(Kind):
    pass
NumKind.kind = NumKind()

class IntKind(Kind):
    pass
IntKind.kind = IntKind()

class BoolKind(Kind):
    pass
BoolKind.kind = BoolKind()

class ArrayKind(Kind):
    def __init__(self, size, kind):
        self.size = size
        self.kind = kind

    def __str__(self):
        return self.node_type() + ": " + str(self.size) + "*" + str(self.kind)

    def visit(self, visitor):
        visitor.enter(self)
        self.kind.visit(visitor)
        visitor.leave(self)

class Klass(Kind):
    def __init__(self, decls, base, name=None):
        self.decls = decls
        self.base = base
        self.name = name

    def __str__(self):
        result = self.node_type() + ": "
        if self.name:
            result += self.name
        if self.base:
            result += " extends " + str(self.base)
        return result

    def visit(self, visitor):
        visitor.enter(self)
        for name, decl in self.decls.items():
            decl.visit(visitor)
        visitor.leave(self)

class Expr(Node):
    def __init__(self, kind):
        self.kind = kind

class UnaryExpr(Expr):
    def __init__(self, kind, op, expr):
        super().__init__(kind)
        self.op = op
        self.expr = expr

    def __str__(self):
        return self.op + self.expr

    def visit(self, visitor):
        visitor.enter(self)
        self.expr.visit(visitor)
        visitor.leave(self)

class BinaryExpr(Expr):
    def __init__(self, kind, lhs, op, rhs):
        super().__init__(kind)
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return "(" + str(self.lhs) + " " + self.op + " " + str(self.rhs) + ")"

    def visit(self, visitor):
        visitor.enter(self)
        self.lhs.visit(visitor)
        self.rhs.visit(visitor)
        visitor.leave(self)

class DotExpr(Expr):
    def __init__(self, kind, expr, member):
        super().__init__(kind)
        self.expr = expr
        self.member = member

    def __str__(self):
        return str(self.expr) + "." + self.member

    def visit(self, visitor):
        visitor.enter(self)
        self.expr.visit(visitor)
        visitor.leave(self)

class BracketExpr(Expr):
    def __init__(self, kind, expr, index):
        super().__init__(kind)
        self.expr = expr
        self.index = index

    def __str__(self):
        return str(self.expr) + "[" + str(self.index) + "]"

    def visit(self, visitor):
        visitor.enter(self)
        self.expr.visit(visitor)
        self.index.visit(visitor)
        visitor.leave(self)

class CallExpr(Expr):
    def __init__(self, expr, args):
        super().__init__(expr.kind.ret if expr.kind else None)
        self.expr = expr
        self.args = args

    def __str__(self):
        return str(self.expr) + "(" + ", ".join(map(str, self.args)) + ")"

    def visit(self, visitor):
        visitor.enter(self)
        self.expr.visit(visitor)
        for arg in self.args:
            arg.visit(visitor)
        visitor.leave(self)

class Literal(Expr):
    pass

class BoolLiteral(Literal):
    def __init__(self, value):
        super().__init__(BoolKind.kind)
        self.value = value

class YesLiteral(BoolLiteral):
    def __init__(self):
        super().__init__(True)

    def __str__(self):
        return "yes"

class NoLiteral(BoolLiteral):
    def __init__(self):
        super().__init__(False)

    def __str__(self):
        return "no"

class NumLiteral(Literal):
    def __init__(self, value):
        super().__init__(IntKind.kind)
        self.value = value

    def __str__(self):
        return str(self.value)

class VarRef(Expr):
    def __init__(self, name, var):
        super().__init__(var.kind if var else None)
        self.name = name
        self.var = var

    def __str__(self):
        return str(self.name)

class FuncRef(Expr):
    def __init__(self, func):
        super().__init__(func.kind)
        self.func = func

    def __str__(self):
        return str(self.var.name)

class Stat(Node):
    pass

class SimpleStat(Stat):
    pass

class AssignStat(SimpleStat):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return str(self.lhs) + " := " + str(self.rhs)

    def visit(self, visitor):
        visitor.enter(self)
        self.lhs.visit(visitor)
        self.rhs.visit(visitor)
        visitor.leave(self)

class ReturnStat(SimpleStat):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return "return " + str(self.expr) + ";"

    def visit(self, visitor):
        visitor.enter(self)
        self.expr.visit(visitor)
        visitor.leave(self)

class PrintStat(SimpleStat):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return "print " + str(self.expr) + ";"

    def visit(self, visitor):
        visitor.enter(self)
        self.expr.visit(visitor)
        visitor.leave(self)

class ExprStat(SimpleStat):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return str(self.expr) + ";"

    def visit(self, visitor):
        visitor.enter(self)
        self.expr.visit(visitor)
        visitor.leave(self)

class IfStat(Stat):
    def __init__(self, expr, stats, branches):
        self.expr = expr
        self.stats = stats
        self.branches = branches

    def __str__(self):
        return self.node_type() + ": " + str(self.expr)

    def visit(self, visitor):
        visitor.enter(self)
        self.expr.visit(visitor)
        for stat in self.stats:
            stat.visit(visitor)
        for stat in self.branches:
            stat.visit(visitor)
        visitor.leave(self)

class IfBranch(Node):
    def __init__(self, expr, stats):
        self.expr = expr
        self.stats = stats

    def __str__(self):
        return self.node_type() + ": " + str(self.expr)

    def visit(self, visitor):
        visitor.enter(self)
        if self.expr:
            self.expr.visit(visitor)
        for stat in self.stats:
            stat.visit(visitor)
        visitor.leave(self)

class WhileStat(Stat):
    def __init__(self, expr, stats):
        self.expr = expr
        self.stats = stats

    def __str__(self):
        return self.node_type() + ": " + str(self.expr)

    def visit(self, visitor):
        visitor.enter(self)
        self.expr.visit(visitor)
        for stat in self.stats:
            stat.visit(visitor)
        visitor.leave(self)

class RepeatStat(Stat):
    def __init__(self, expr, stats):
        self.expr = expr
        self.stats = stats

    def __str__(self):
        return self.node_type() + ": (POST) " + str(self.expr)

    def visit(self, visitor):
        visitor.enter(self)
        self.expr.visit(visitor)
        for stat in self.stats:
            stat.visit(visitor)
        visitor.leave(self)

class ForeachStat(Stat):
    def __init__(self, var, expr, stats):
        self.var = var
        self.expr = expr
        self.stats = stats

    def __str__(self):
        return self.node_type() + ": " + self.var.name + " in " + str(self.expr)

    def visit(self, visitor):
        visitor.enter(self)
        self.expr.visit(visitor)
        for stat in self.stats:
            stat.visit(visitor)
        visitor.leave(self)
