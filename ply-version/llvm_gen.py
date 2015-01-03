from llvm import *
from llvm.core import *
from syntax_tree import *

class Symbol(object):
    def getVal(self, builder):
        pass
    def getAddr(self):
        pass

class IntType(Symbol):
    def __init__(self, builder, name):
        self.name = name
        self.var = builder.alloca(Type.int(32), name)
    def getVal(self, builder):
        return builder.load(self.var, self.name)

    def getAddr(self):
        return self.var


class LLVMGenerator(object):
    def __init__(self):
        self.var_stack = []
        self.kind_stack = []
        self.llvm_module = None
        self.builder = None

    def progLLVM(self, progNode):
        self.llvm_module = Module.new(progNode.name)
        self.var_stack.append({})
        self.declLLVM(progNode.decls)
        self.progImplLLVM(progNode.impl)
        print(self.llvm_module)

    def declLLVM(self, declNode):
        for name, decl in declNode.items():
            if(isinstance(decl, FuncDecl)):
                self.funcLLVM(decl)
            elif(isinstance(decl, KindDecl)):
                continue

    def funcLLVM(self, funcNode):
    # declare the function
        func_type = Type.function(funcNode.kind.ret.llvm_type,
                funcNode.kind.arg_llvm_type())
        func = Function.new(self.llvm_module, func_type, funcNode.name)
        
        entry = func.append_basic_block('entry')
        self.builder = Builder.new(entry)
    # enter the function scope
        self.var_stack.append(dict(self.var_stack[-1]))
        
    # create argument allocas
        for arg, arg_decl in zip(func.args, funcNode.args.decl_list):
            arg.name = arg_decl.name
            alloca = self.builder.alloca(arg_decl.kind.llvm_type, None, arg_decl.name)
            self.builder.store(arg, alloca)
            self.var_stack[-1][arg_decl.name] = alloca

    # implement the function node
        self.funcImplLLVM(func, funcNode.impl)

    # leave the function scope
        self.var_stack.pop()

    def funcImplLLVM(self, func, implNode):
        self.varDeclsLLVM(func, implNode.vars)
        self.statsLLVM(func, implNode.stats)
    
    def varDeclsLLVM(self, func, varDecls):
        for name, varDecl in varDecls.items():
            self.var_stack[-1][varDecl.name] = self.builder.alloca(varDecl.kind.llvm_type, None, name)

    def statsLLVM(self, func, stats):
        for stat in stats:
            if isinstance(stat, AssignStat):
                self.assignStatLLVM(func, stat)
            elif isinstance(stat, ReturnStat):
                self.returnStatLLVM(func, stat)
            elif isinstance(stat, PrintStat):
                self.printStatLLVM(func, stat)
            elif isinstance(stat, ExprStat):
                self.exprStatLLVM(stat)
            elif isinstance(stat, IfStat):
                self.ifStatLLVM(func, stat)
            elif isinstance(stat, WhileStat):
                self.whileStatLLVM(func, stat)
            elif isinstance(stat, RepeatStat):
                self.repeatStatLLVM(func, stat)
            elif isinstance(stat, ForeachStat):
                self.foreachStatLLVM(func, stat)
            else:
                print(type(stat))
                raise Exception()

    def assignStatLLVM(self, func, assignStat):
        if isinstance(assignStat.lhs, VarRef):
            if assignStat.lhs.name in self.var_stack[-1]:
                var_addr = self.var_stack[-1][assignStat.lhs.name]
            else:
                print("No such variable {0}".format(assignStat.lhs.name))
            result = self.exprStatLLVM(assignStat.rhs)
            self.builder.store(result, var_addr)
        else:
            print("invalid assignment lhs")
            raise Exception()

    def returnStatLLVM(self, func, returnStat):
        if returnStat.expr != None:
            result = self.exprStatLLVM(returnStat.expr)
            self.builder.ret(result)
        else:
            self.builder.ret_void()

    def printStatLLVM(self, func, printStat):
        return

    def exprStatLLVM(self, exprStat):
        if isinstance(exprStat, UnaryExpr):
            return self.unaryExprLLVM(exprStat)
        elif isinstance(exprStat, BinaryExpr):
            return self.binaryExprLLVM(exprStat)
        elif isinstance(exprStat, DotExpr):
            return self.dotExprLLVM(exprStat)
        elif isinstance(exprStat, BracketExpr):
            return self.bracketExpr(exprStat)
        elif isinstance(exprStat, CallExpr):
            return self.callExprLLVM(exprStat)
        elif isinstance(exprStat, MethodExpr):
            return self.methodExprLLVM(exprStat)
        elif isinstance(exprStat, (BoolLiteral, NumLiteral)):
            return exprStat.llvm_type
        elif isinstance(exprStat, VarRef):
            return self.varRefLLVM(exprStat)
    
    def unaryExprLLVM(self, unaryExpr):
        expr = self.exprStatLLVM(unaryExpr.expr)
        
        if unaryExpr.op == "not":
            result = self.builder.icmp(ICMP_EQ, expr, Constant.int(Type.int(32), 0), "not_expr")
        elif unaryExpr.op == "+":
            result = expr
        elif unaryExpr.op == "-":
            result = self.builder.neg(expr, "neg_expr")
        
        return result;

    def binaryExprLLVM(self, binaryExpr):
        lhs = self.exprStatLLVM(binaryExpr.lhs)
        rhs = self.exprStatLLVM(binaryExpr.rhs)
        if binaryExpr.op == "+":
            result = self.builder.add(lhs, rhs, "add_expr")
        elif binaryExpr.op == "-":
            result = self.builder.sub(lhs, rhs, "sub_expr")
        elif binaryExpr.op == "*":
            result = self.builder.mul(lhs, rhs, "mul_expr")
        elif binaryExpr.op == "/":
            result = self.builder.sdiv(lhs, rhs, "sdiv_expr")
        elif binaryExpr.op == "%":
            result = self.builder.srem(lhs, rhs, "srem_expr")
        elif binaryExpr.op == "==":
            result = self.builder.icmp(ICMP_EQ, lhs, rhs, "eq_expr")
        elif binaryExpr.op == "!=":
            result = self.builder.icmp(ICMP_NE, lhs, rhs, "ne_expr")
        elif binaryExpr.op == "<":
            result = self.builder.icmp(ICMP_SLT, lhs, rhs, "slt_expr")
        elif binaryExpr.op == "<=":
            result = self.builder.icmp(ICMP_SLE, lhs, rhs, "sle_expr")
        elif binaryExpr.op == ">":
            result = self.builder.icmp(ICMP_SGT, lhs, rhs, "sgt_expr")
        elif binaryExpr.op == ">=":
            result = self.builder.icmp(ICMP_SGE, lhs, rhs, "sge_expr")
        elif binaryExpr.op == "and":
            lhs_bool = self.builder.icmp(ICMP_NE, lhs, Constant.int(Type.int(32), 0), "lhs_bool")
            rhs_bool = self.builder.icmp(ICMP_NE, rhs, Constant.int(Type.int(32), 0), "rhs_bool")
            result = self.builder.and_(lhs_bool, rhs_bool, "and_expr")
        elif binaryExpr.op == "or":
            lhs_bool = self.builder.icmp(ICMP_NE, lhs, Constant.int(Type.int(32), 0), "lhs_bool")
            rhs_bool = self.builder.icmp(ICMP_NE, rhs, Constant.int(Type.int(32), 0), "rhs_bool")
            result = self.builder.or_(lhs_bool, rhs_bool, "or_expr")
        else:
            print("no such operand {0}".format(binaryExpr.op))
            raise Exception()

        return result;

    def dotExprLLVM(self, dotExpr):
        return Constant.int(Type.int(32), 1)

    def bracketExprLLVM(self, bracketExpr):
        return Constant.int(Type.int(32), 1)

    def callExprLLVM(self, callExpr):
        callee = self.llvm_module.get_function_named(callExpr.expr.name)
        arg_exprs = [ self.exprStatLLVM(arg) for arg in callExpr.args ]
        return self.builder.call(callee, arg_exprs, 'call_' + callExpr.expr.name)

    def methodExprLLVM(self, methodEpxr):
        return Constant.int(Type.int(32), 1)

    def varRefLLVM(self, varRef):
        if varRef.name in self.var_stack[-1]:
            var_addr = self.var_stack[-1][varRef.name]
            result = self.builder.load(var_addr, varRef.name)
        else:
            print("not variable named: {0}".format(varRef.name))
            raise Exception()

        return result

    def ifStatLLVM(self, func, ifStat):
        ifBranches = []
    # build blocks
        if_block = func.append_basic_block('if')
        then_block = func.append_basic_block('then')
        
        for ifBranch in ifStat.branches:
            if ifBranch.expr == None:
                elif_block = None
                else_block = func.append_basic_block('else')
            else:
                elif_block = func.append_basic_block('elif')
                else_block = func.append_basic_block('then')
            ifBranches.append([elif_block ,else_block, ifBranch])

        end_block = func.append_basic_block('end_if')
        
    # implement the blocks
        # switch to if
        self.builder.branch(if_block)
        # implement if_block
        self.builder.position_at_end(if_block)
        result = self.exprStatLLVM(ifStat.expr)
        if len(ifBranches) == 0:
            self.builder.cbranch(result, then_block, end_block)
        else:
            self.builder.cbranch(result, then_block, ifBranches[0][0])
        
        # implement then_block
        self.builder.position_at_end(then_block)
        self.statsLLVM(func, ifStat.stats)
        self.builder.branch(end_block)
        
        # implement else_block 
        while len(ifBranches) > 0:
            ifBranch = ifBranches[0]
            if len(ifBranches) > 1:
                self.builder.position_at_end(ifBranch[0])
                result = self.exprStatLLVM(ifBranch[2].expr)
                if ifBranches[1][0] == None:
                    self.builder.cbranch(result, ifBranch[1], ifBranches[1][1])
                else:
                    self.builder.cbranch(result, ifBranch[1], ifBranches[1][0])
                
            self.builder.position_at_end(ifBranch[1])
            self.statsLLVM(func, ifBranch[2].stats)
            self.builder.branch(end_block)
            ifBranches = ifBranches[1:]

        self.builder.position_at_end(end_block)
                
    def whileStatLLVM(self, func, whileStat):
    #build blocks
        while_block = func.append_basic_block("while")
        body_block = func.append_basic_block("loop_body")
        end_block = func.append_basic_block("end_while")
    #implement
        self.builder.branch(while_block)
        self.builder.position_at_end(while_block)
        result = self.exprStatLLVM(whileStat.expr)
        self.builder.cbranch(result, body_block, end_block)

        self.builder.position_at_end(body_block)
        self.statsLLVM(func, whileStat.stats)
        self.builder.branch(while_block)

        self.builder.position_at_end(end_block)

    def repeatStatLLVM(self, func, repeatStat):
    #build_blocks
        repeat_block = func.append_basic_block("repeat")
        until_block = func.append_basic_block("until")
        end_block = func.append_basic_block("end_repeat")
    #implement
        self.builder.branch(repeat_block)
        self.builder.position_at_end(repeat_block)
        self.statsLLVM(func, repeatStat.stats)
        self.builder.branch(until_block)

        self.builder.position_at_end(until_block)
        result = self.exprStatLLVM(repeatStat.expr)
        self.builder.cbranch(result, end_block, repeat_block)

        self.builder.position_at_end(end_block)

    def foreachStatLLVM(self, func, foreachStat):
        return

    def progImplLLVM(self, implNode):
        funct_type = Type.function(Type.void(), tuple())
        func = Function.new(self.llvm_module, funct_type, "main")
        self.var_stack.append(dict(self.var_stack[-1]))
        
        entry = func.append_basic_block('entry')
        self.builder = Builder.new(entry)
        self.varDeclsLLVM(func, implNode.vars)
        self.statsLLVM(func, implNode.stats)
        
        self.var_stack.pop()
        self.builder.ret_void()
