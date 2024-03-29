#!/usr/bin/python3
import ply.yacc as yacc

from lexer import tokens
from syntax_tree import *
from syntax_tree_print import *

class MyLangAnalyzeException(Exception):
    pass

class UnknownKindException(MyLangAnalyzeException):
    def __init__(self, name):
        self.name = name
        super().__init__('Unknown kind "{0}"!'.format(name))

class UndefinedVarException(MyLangAnalyzeException):
    def __init__(self, name):
        self.name = name
        super().__init__('Undefined variable "{0}"!'.format(name))

class KindResolvingVisitor(NodeVisitor):
    def __init__(self):
        self.kind_stack = []
        self.klass = None
        self.klass_of = {}

    def resolve_kind(self, name):
        kind = self.kind_stack[-1].get(name)
        if kind is None:
            raise UnknownKindException(name)
        return kind

    def get_klass(self, node):
        klass = self.klass_of.get(node)
        if klass: return klass

        klass = node.to_klass()
        vars = {}
        methods = {}
        self.klass = klass
        for name, kind in klass.vars.items():
            vars[name] = kind.visit(self)
        for name, method in klass.methods.items():
            methods[name] = method.visit(self)
        self.klass = None
        klass.vars = vars
        klass.methods = methods
        self.klass_of[node] = klass

        return klass

    def enter(self, node):
        if isinstance(node, KindRef):
            result = self.resolve_kind(node.name)
            if not isinstance(result, Klass):
                result = result.visit(self)
            return result
        elif isinstance(node, Program):
            self.kind_stack.append({
                'boolean': BoolKind.kind,
                'integer': IntKind.kind,
            })
            for name, decl in node.decls.items():
                if isinstance(decl, KindDecl):
                    kind = decl.kind
                    if isinstance(kind, KlassDecl):
                        kind = self.get_klass(kind)
                    self.kind_stack[-1][name] = kind
        elif isinstance(node, KlassDecl):
            return self.get_klass(node)
        if isinstance(node, Klass):
            if node.base:
                if isinstance(node.base, KindRef):
                    node.base = node.base.visit(self)
                # Make derived class inherit vars in base class.
                vars = node.base.vars.copy()
                vars.update(node.vars)
                node.vars = vars
        elif isinstance(node, ArgList):
            if self.klass is not None:
                if not node.decl_list or node.decl_list[0].name != 'class':
                    klass_arg = VarDecl('class', self.klass)
                    return ArgList([klass_arg] + node.decl_list)

        return node

    def leave(self, node):
        if isinstance(node, Program):
            self.kind_stack.pop()

        return node

class NotCallableException(MyLangAnalyzeException):
    def __init__(self, expr):
        self.expr = expr
        super().__init__(
                'Expression {0} <{1}> is not callable.'.format(
                expr, expr.kind))

class CallArgCountException(MyLangAnalyzeException):
    def __init__(self, expr, expected, actual):
        self.expr = expr
        self.expected = expected
        self.actual = actual
        super().__init__(
                '{0} takes exactly {1} argument(s) ({2} given).'.format(
                expr, expected, actual))

class CallKindException(MyLangAnalyzeException):
    def __init__(self, expr, index, expected, actual):
        self.expr = expr
        self.index = index
        self.expected = expected
        self.actual = actual
        super().__init__((
                'No matching call to {0} {1}.\n' +
                '\tCannot convert {4} to {3} for Argument {2}.'
            ).format(expr, expr.kind, index, expected, actual))

class NotScriptableException(MyLangAnalyzeException):
    def __init__(self, expr):
        self.expr = expr
        super().__init__(
                'Expression {0} <{1}> is not scriptable.'.format(
                expr, expr.kind))

class IndexKindException(MyLangAnalyzeException):
    def __init__(self, expr):
        self.expr = expr
        super().__init__(
                'Array index {0} must be integer, not {1}'.format(
                expr, expr.kind))

class OperatorOverloadException(MyLangAnalyzeException):
    def __init__(self, op, args):
        self.op = op
        self.args = args
        super().__init__(
                'No matching operator {0} found for types {1}'.format(
                    op, ', '.join(map(lambda a: str(a.kind), args))))

class VarResolvingVisitor(NodeVisitor):
    def __init__(self):
        self.var_stack = []

        int__int_int = FuncKind(IntKind.kind, [IntKind.kind, IntKind.kind])
        bool__int_int = FuncKind(BoolKind.kind, [IntKind.kind, IntKind.kind])
        bool__bool_bool = FuncKind(BoolKind.kind,
                [BoolKind.kind, BoolKind.kind])

        unary_operators = {
                '+': [FuncKind(IntKind.kind, [IntKind.kind])],
                '-': [FuncKind(IntKind.kind, [IntKind.kind])],
                'not': [FuncKind(BoolKind.kind, [BoolKind.kind])],
        }
        binary_operators = {
                '+': [int__int_int],
                '-': [int__int_int],
                '*': [int__int_int],
                '/': [int__int_int],
                '%': [int__int_int],
                '==': [bool__int_int, bool__bool_bool],
                '!=': [bool__int_int, bool__bool_bool],
                '<': [bool__int_int],
                '<=': [bool__int_int],
                '>': [bool__int_int],
                '>=': [bool__int_int],
                'and': [bool__bool_bool],
                'or': [bool__bool_bool],
        }

        self.operator_overloads = [{}, unary_operators, binary_operators]

    def resolve_var(self, name):
        var = self.var_stack[-1].get(name)
        if var is None:
            raise UndefinedVarException(name)
        return var

    def _add_members(self, klass):
        for name in klass.vars.keys():
            self.var_stack[-1][name] = 'class var'
        for name, decl in klass.methods.items():
            self.var_stack[-1][name] = decl

    def resolve_operator(self, op, args):
        count = len(args)
        if count > len(self.operator_overloads):
            raise MyLangAnalyzeException(
                    "No operator defined for {0} args!".format(count))
        overloads = self.operator_overloads[count].get(op)
        if overloads:
            for func in overloads:
                match = True
                for i in range(count):
                    if args[i].kind != func.arg_kinds[i]:
                        match = False
                        break
                if match:
                    return func.ret

        raise OperatorOverloadException(op, args)

    def enter(self, node):
        if isinstance(node, Program):
            self.var_stack.append({})
            for name, decl in node.decls.items():
                if isinstance(decl, FuncDecl):
                    self.var_stack[-1][name] = decl
        elif isinstance(node, FuncDecl):
            self.var_stack.append(dict(self.var_stack[-1]))
        elif isinstance(node, Impl):
            self.var_stack.append(dict(self.var_stack[-1]))
        elif isinstance(node, Klass):
            self.var_stack.append(dict(self.var_stack[-1]))
            self.klass_scope = self.var_stack[-1]
            self.klass = node
            if node.base:
                self._add_members(node.base)
            self._add_members(node)
        elif isinstance(node, VarRef):
            node.var = self.resolve_var(node.name)
            if node.var == 'class var':
                # Replace instance variable reference with explicit DotExpr.
                return DotExpr(VarRef('class', self.klass), node.name)
            node.kind = node.var.kind
        elif isinstance(node, ForeachStat):
            # foreach i in range(10) do
            if (isinstance(node.expr, CallExpr) and
                isinstance(node.expr.expr, VarRef) and
                node.expr.expr.name == 'range'):
                args = node.expr.args
                if len(args) == 1:
                    from_expr = NumLiteral(0)
                    to_expr = args[0]
                else:
                    from_expr, to_expr = args
                init_st = AssignStat(node.var, from_expr)
                inc = BinaryExpr(node.var, '+', NumLiteral(1))
                stats = node.stats + [AssignStat(node.var, inc)]
                while_st = WhileStat(BinaryExpr(node.var, '<', to_expr), stats)
                return RepeatStat(BoolLiteral.yes, [init_st, while_st])

        return node

    def leave(self, node):
        if isinstance(node, Program):
            self.var_stack.pop()
            self.node_scope = {}
        elif isinstance(node, Impl):
            self.var_stack.pop()
        elif isinstance(node, Klass):
            self.var_stack.pop()
            self.klass = None
        elif isinstance(node, FuncDecl):
            self.var_stack.pop()
        elif isinstance(node, VarDecl):
            self.var_stack[-1][node.name] = node
        elif isinstance(node, DotExpr):
            klass = node.expr.kind
            node.kind = klass.vars.get(node.member)
            if node.kind is None:
                method = klass.methods[node.member]
                # Replace method retrieval with explicit MethodExpr.
                return MethodExpr(klass, method)
        elif isinstance(node, CallExpr):
            if not isinstance(node.expr.kind, FuncKind):
                raise NotCallableException(node.expr)
            arg_kinds = node.expr.kind.arg_kinds
            arg_len = len(arg_kinds)
            if len(node.args) != arg_len:
                raise CallArgCountException(node.expr, arg_len, len(node.args))
            for i in range(arg_len):
                if node.args[i].kind != arg_kinds[i]:
                    raise CallKindException(node.expr, i, arg_kinds[i],
                            node.args[i].kind)
            node.kind = node.expr.kind.ret
        elif isinstance(node, BracketExpr):
            if not isinstance(node.expr.kind, ArrayKind):
                raise NotScriptableException(node.expr)
            if node.index.kind != IntKind.kind:
                raise IndexKindException(node.index)
            node.kind = node.expr.kind.kind
        elif isinstance(node, BinaryExpr):
            node.kind = self.resolve_operator(node.op, [node.lhs, node.rhs])
        elif isinstance(node, UnaryExpr):
            node.kind = self.resolve_operator(node.op, [node.expr])

        return node

def analyze(prog):
    prog = prog.visit(KindResolvingVisitor())
    prog = prog.visit(VarResolvingVisitor())
    return prog
