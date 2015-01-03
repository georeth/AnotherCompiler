#!/usr/bin/python3

from llvm.core import *

class NodeVisitor(object):
    def enter(self, node):
        return node
    def leave(self, node):
        return node

class Node(object):
    def node_type(self):
        return type(self).__name__

    def __str__(self):
        return self.node_type()

    def visit(self, visitor, filter=None):
        while filter is None or filter(self):
            old_self = self
            self = visitor.enter(self)
            if self == old_self: break
        if filter is None or filter(self):
            self = self._visit(visitor)
            return visitor.leave(self)
        else:
            return self

    def _visit(self, visitor):
        return self

    @classmethod
    def _is_kind_ref(self, node):
        return isinstance(node, KindRef)

    def _visit_kind_ref(self, visitor):
        return self.visit(visitor, Node._is_kind_ref)

    def _visit_list(self, l, visitor, filter=None):
        result = l
        for i, value in enumerate(l):
            new_value = value.visit(visitor, filter)
            if new_value != value:
                if result is l:
                    result = l.copy()
                result[i] = new_value
        return result

    def _visit_dict(self, d, visitor, filter=None):
        result = d
        for key, value in d.items():
            new_value = value.visit(visitor, filter)
            if new_value != value:
                if result is d:
                    result = d.copy()
                result[key] = new_value
        return result

class Kind(Node):
    def __str__(self):
        return 'type'

class NumKind(Kind):
    def __str__(self):
        return 'num'

NumKind.kind = NumKind()

class IntKind(Kind):
    def __init__(self):
        self.llvm_type = Type.int(32)

    def __str__(self):
        return 'integer'

IntKind.kind = IntKind()

class BoolKind(IntKind):
    def __init__(self):
        self.llvm_type = Type.int(1)
    def __str__(self):
        return 'boolean'

BoolKind.kind = BoolKind()

class ArrayKind(Kind):
    def __init__(self, size, kind):
        self.size = size
        self.kind = kind
        if isinstance(kind, Kind):
            self.llvm_type = Type.array(kind.llvm_type, size)
    def __str__(self):
        return str(self.kind) + '[' + str(self.size) + ']'

    def _visit(self, visitor):
        kind = self.kind._visit_kind_ref(visitor)
        if kind != self.kind:
            self = ArrayKind(self.size, kind)
        return self

    def __eq__(self, other):
        if not isinstance(other, ArrayKind): return False
        return self.size == other.size and self.kind == other.kind

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((size, kind,))

class FuncKind(Kind):
    def __init__(self, ret, arg_kinds):
        self.ret = ret
        self.arg_kinds = arg_kinds

    def arg_llvm_type(self):
        return tuple(map(lambda kind: kind.llvm_type, self.arg_kinds))

    def __str__(self):
        arg_kinds_str = ', '.join(map(str, self.arg_kinds))
        ret_str = str(self.ret) if self.ret else ''
        return 'function<' + ret_str + '(' + arg_kinds_str + ')>'

    def _visit(self, visitor):
        ret = self.ret._visit_kind_ref(visitor)
        arg_kinds = self._visit_list(self.arg_kinds, visitor, Node._is_kind_ref)
        if kind != self.kind or ret != self.ret:
            self = FuncKind(ret, arg_kinds)
        return self

    def __eq__(self, other):
        if not isinstance(other, FuncKind): return False
        return self.ret == other.ret and self.arg_kinds == other.arg_kinds

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hast((ret, tuple(self.arg_kinds),))

class Klass(Kind):
    def __init__(self, base, vars, methods, name=None):
        self.base = base
        self.vars = vars
        self.methods = methods
        self.name = name

    def __str__(self):
        return "class " + self.name

    def _visit(self, visitor):
        if self.base is None:
            base = self.base
        else:
            base = self.base._visit_kind_ref(visitor)
        vars = self._visit_dict(self.vars, visitor, Node._is_kind_ref)
        methods = self._visit_dict(self.methods, visitor)

        if (base is not self.base or vars is not self.vars or
                methods is not self.methods):
            self = Klass(base, vars, methods, self.name)

        return self

class Program(Node):
    def __init__(self, name, args, decls, impl):
        self.name = name
        self.args = args
        self.decls = decls
        self.impl = impl

    def __str__(self):
        return self.node_type() + ": " + self.name + " "

    def _visit(self, visitor):
        args = self.args.visit(visitor)
        decls = self._visit_dict(self.decls, visitor)
        impl = self.impl.visit(visitor)

        if decls is not self.decls or impl != self.impl or args != self.args:
            self = Program(self.name, args, decls, impl)

        return self

class FuncDecl(Node):
    def __init__(self, name, args, ret, impl):
        self.name = name
        self.args = args
        self.ret = ret
        self.impl = impl
        arg_kinds = list(map(lambda decl: decl.kind, self.args.decl_list))
        self.kind = FuncKind(ret, arg_kinds)

    def __str__(self):
        return self.node_type() + ": " + self.name

    def _visit(self, visitor):
        args = self.args.visit(visitor)
        if self.ret is None:
            ret = self.ret
        else:
            ret = self.ret._visit_kind_ref(visitor)
        impl = self.impl.visit(visitor)

        if impl != impl or args != self.args or impl != self.impl:
            self = FuncDecl(self.name, args, ret, impl)

        return self

class ArgList(Node):
    def __init__(self, decl_list):
        self.decl_list = decl_list
        self.names = list(map(lambda decl: decl.name, decl_list))

    def __str__(self):
        return self.node_type() + ": " + ", ".join(self.names)

    def _visit(self, visitor):
        decl_list = self._visit_list(self.decl_list, visitor)

        if decl_list is not self.decl_list:
            self = ArgList(decl_list)

        return self

class Impl(Node):
    def __init__(self, vars, stats):
        self.vars = vars
        self.stats = stats

    def _visit(self, visitor):
        vars = self._visit_dict(self.vars, visitor)
        stats = self._visit_list(self.stats, visitor)

        if vars is not self.vars or stats is not self.stats:
            self = Impl(vars, stats)

        return self

class VarDecl(Node):
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind

    def __str__(self):
        return self.node_type() + ": " + self.name + " " + str(self.kind)

    def _visit(self, visitor):
        kind = self.kind._visit_kind_ref(visitor)

        if kind != self.kind:
            self = VarDecl(self.name, kind)

        return self

class KindDecl(Node):
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind

    def __str__(self):
        return self.node_type() + ": " + self.name

    def _visit(self, visitor):
        if (isinstance(self.kind, (Klass, KlassDecl)) and
                self.name == self.kind.name):
            # Visit Klass declaration.
            kind = self.kind.visit(visitor)
        else:
            kind = self.kind._visit_kind_ref(visitor)

        if kind != self.kind:
            self = KindDecl(self.name, kind)

        return self

class KlassDecl(Node):
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

    def _visit(self, visitor):
        if self.base is None:
            base = self.base
        else:
            base = self.base._visit_kind_ref(visitor)
        decls = self._visit_dict(self.decls, visitor)

        if decls is not self.decls or base is not self.base:
            self = KlassDecl(decls, base, self.name)

        return self

    def to_klass(self):
        vars = {}
        methods = {}
        for name, decl in self.decls.items():
            if isinstance(decl, VarDecl):
                vars[decl.name] = decl.kind
            elif isinstance(decl, FuncDecl):
                methods[decl.name] = decl
        return Klass(self.base, vars, methods, self.name)

class KindRef(Node):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "&" + self.name

class Expr(Node):
    def __init__(self, kind=None):
        self.kind = kind

class UnaryExpr(Expr):
    def __init__(self, op, expr):
        super().__init__()
        self.op = op
        self.expr = expr

    def __str__(self):
        return self.op + str(self.expr)

    def _visit(self, visitor):
        expr = self.expr.visit(visitor)

        if expr != self.expr:
            self = UnaryExpr(self.op, expr)

        return self

class BinaryExpr(Expr):
    def __init__(self, lhs, op, rhs):
        super().__init__()
        self.op = op
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return "(" + str(self.lhs) + " " + self.op + " " + str(self.rhs) + ")"

    def _visit(self, visitor):
        lhs = self.lhs.visit(visitor)
        rhs = self.rhs.visit(visitor)

        if lhs != self.lhs or rhs != self.rhs:
            self = BinaryExpr(lhs, self.op, rhs)

        return self

class DotExpr(Expr):
    def __init__(self, expr, member):
        super().__init__()
        self.expr = expr
        self.member = member

    def __str__(self):
        return str(self.expr) + "." + self.member

    def _visit(self, visitor):
        expr = self.expr.visit(visitor)

        if expr != self.expr:
            self = DotExpr(expr, member)

        return self

class BracketExpr(Expr):
    def __init__(self, expr, index):
        super().__init__()
        self.expr = expr
        self.index = index

    def __str__(self):
        return str(self.expr) + "[" + str(self.index) + "]"

    def _visit(self, visitor):
        expr = self.expr.visit(visitor)
        index = self.index.visit(visitor)

        if expr != self.expr or index != self.index:
            self = BracketExpr(expr, index)

        return self

class CallExpr(Expr):
    def __init__(self, expr, args):
        super().__init__()
        self.expr = expr
        self.args = args

    def __str__(self):
        return str(self.expr) + "(" + ", ".join(map(str, self.args)) + ")"

    def _visit(self, visitor):
        expr = self.expr.visit(visitor)
        args = self._visit_list(self.args, visitor)

        if expr != self.expr or args is not self.args:
            self = CallExpr(expr, args)

        return self

class MethodExpr(Expr):
    def __init__(self, klass, method):
        super().__init__()
        self.klass = klass
        self.method = method
        self.kind = self.method.kind

    def __str__(self):
        return self.klass.name + '::' + self.method.name

class Literal(Expr):
    pass

class BoolLiteral(Literal):
    def __init__(self, value):
        super().__init__(BoolKind.kind)
        self.value = value
        self.llvm_type = Constant.int(Type.int(1), value)

class YesLiteral(BoolLiteral):
    def __init__(self):
        super().__init__(1)

    def __str__(self):
        return "yes"

class NoLiteral(BoolLiteral):
    def __init__(self):
        super().__init__(0)

    def __str__(self):
        return "no"

class NumLiteral(Literal):
    def __init__(self, value):
        super().__init__(IntKind.kind)
        self.value = value
        self.llvm_type = Constant.int(Type.int(32), value)

    def __str__(self):
        return str(self.value)

class VarRef(Expr):
    def __init__(self, name, var):
        super().__init__()
        self.name = name
        self.var = var

    def __str__(self):
        return str(self.name)

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

    def _visit(self, visitor):
        lhs = self.lhs.visit(visitor)
        rhs = self.rhs.visit(visitor)

        if lhs != self.lhs or rhs != self.rhs:
            self = AssignStat(lhs, rhs)

        return self

class ReturnStat(SimpleStat):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return "return " + str(self.expr) + ";"

    def _visit(self, visitor):
        expr = self.expr.visit(visitor)

        if expr != self.expr:
            self = ReturnStat(expr)

        return self

class PrintStat(SimpleStat):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return "print " + str(self.expr) + ";"

    def _visit(self, visitor):
        expr = self.expr.visit(visitor)

        if expr != self.expr:
            self = PrintStat(expr)

        return self

class ExprStat(SimpleStat):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return str(self.expr) + ";"

    def _visit(self, visitor):
        expr = self.expr.visit(visitor)

        if expr != self.expr:
            self = ExprStat(expr)

        return self

class IfStat(Stat):
    def __init__(self, expr, stats, branches):
        self.expr = expr
        self.stats = stats
        self.branches = branches

    def __str__(self):
        return self.node_type() + ": " + str(self.expr)

    def _visit(self, visitor):
        expr = self.expr.visit(visitor)
        stats = self._visit_list(self.stats, visitor)
        branches = self._visit_list(self.branches, visitor)

        if (expr != self.expr or stats is not self.stats or
                branches is not self.branches):
            self = IfStat(expr, stats, branches)

        return self

class IfBranch(Node):
    def __init__(self, expr, stats):
        self.expr = expr
        self.stats = stats

    def __str__(self):
        return self.node_type() + ": " + str(self.expr)

    def _visit(self, visitor):
        if self.expr:
            expr = self.expr.visit(visitor)
        else:
            expr = None

        stats = self._visit_list(self.stats, visitor)

        if (expr != self.expr or stats is not self.stats):
            self = IfBranch(expr, stats)

        return self

class WhileStat(Stat):
    def __init__(self, expr, stats):
        self.expr = expr
        self.stats = stats

    def __str__(self):
        return self.node_type() + ": " + str(self.expr)

    def _visit(self, visitor):
        if self.expr:
            expr = self.expr.visit(visitor)
        else:
            expr = None

        stats = self._visit_list(self.stats, visitor)

        if (expr != self.expr or stats is not self.stats):
            self = IfBranch(expr, stats)

        return self

class RepeatStat(Stat):
    def __init__(self, expr, stats):
        self.expr = expr
        self.stats = stats

    def __str__(self):
        return self.node_type() + ": (POST) " + str(self.expr)

    def _visit(self, visitor):
        if self.expr:
            expr = self.expr.visit(visitor)
        else:
            expr = None

        stats = self._visit_list(self.stats, visitor)

        if (expr != self.expr or stats is not self.stats):
            self = IfBranch(expr, stats)

        return self

class ForeachStat(Stat):
    def __init__(self, var, expr, stats):
        self.var = var
        self.expr = expr
        self.stats = stats

    def __str__(self):
        return self.node_type() + ": " + self.var.name + " in " + str(self.expr)

    def _visit(self, visitor):
        if self.expr:
            expr = self.expr.visit(visitor)
        else:
            expr = None

        stats = self._visit_list(self.stats, visitor)

        if (expr != self.expr or stats is not self.stats):
            self = IfBranch(expr, stats)

        return self
