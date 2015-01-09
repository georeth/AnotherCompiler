from llvm.core import *
from syntax_tree import *

class LLVMGenerator(object):
    def __init__(self):
        self.var_stack = []
        self.kind_stack = []
        self.llvm_module = None
        self.builder = None

    def progLLVM(self, progNode):
        self.llvm_module = Module.new(progNode.name)
    # enter the prog scope
        self.var_stack.append({})
        self.kind_stack.append({})
    # declare the print function
        print_type = Type.function(Type.int(32), [Type.pointer(Type.int(8)),], True)
        self.print_int = self.llvm_module.add_function(print_type, "printf")
    # prepare the format string
        format_str_data = Constant.stringz("%d\n")
        format_array = self.llvm_module.add_global_variable(format_str_data.type, "format_str")
        format_array.initializer = format_str_data
        format_array.global_constant = True
        self.format_str = format_array.gep([Constant.int(Type.int(32), 0), Constant.int(Type.int(32), 0)])
    
    # implement the code
        self.declLLVM(progNode.decls)
        self.declImplLLVM(progNode.decls)
        self.progImplLLVM(progNode.impl)
        print(self.llvm_module)
    # exit the prog scope
        self.var_stack.pop()
        self.kind_stack.pop()
    
    def declImplLLVM(self, declNode):
        for name, decl in declNode.items():
            if isinstance(decl, FuncDecl):
                self.funcLLVM(decl)
            elif isinstance(decl, KindDecl):
                self.kindLLVM(decl)
    
    def declLLVM(self, declNode):
        for name, decl in declNode.items():
            if isinstance(decl, FuncDecl):
                self.funcDeclLLVM(decl)
            elif isinstance(decl, KindDecl):
                self.kindDeclLLVM(decl)            
   
    def kindDeclLLVM(self, kindNode):
        if isinstance(kindNode.kind, Klass):
            self.classDeclLLVM(kindNode.kind)
    
    def kindLLVM(self, kindNode):
        if isinstance(kindNode.kind, Klass):
            self.classLLVM(kindNode.kind)

    def classLLVM(self, classDecl):
        for name, decl in classDecl.methods.items():
            self.funcLLVM(decl, classDecl.name + "::")

    def classDeclLLVM(self, classDecl):
        member_dict = {}
        type_list = classDecl.llvm_type_list()

        for i in range(0, len(type_list)):
            member_dict[type_list[i][0]] = i
        self.kind_stack[-1][classDecl.name] = member_dict 

        for name, decl in classDecl.methods.items():
            self.funcDeclLLVM(decl, classDecl.name + "::")

    def funcDeclLLVM(self, funcNode, className=""):
    # declare the function
        if(funcNode.kind.ret == None):
            return_type = Type.void()
        else:
            return_type = funcNode.kind.ret.llvm_type()
        func_type = Type.function(return_type, funcNode.kind.args_llvm_type())
        func = Function.new(self.llvm_module, func_type, className + funcNode.name)

    def funcLLVM(self, funcNode, className=""):
        if(funcNode.kind.ret == None):
            return_type = Type.void()
        else:
            return_type = funcNode.kind.ret.llvm_type()

        func = self.llvm_module.get_function_named(className + funcNode.name)  
        entry = func.append_basic_block('entry')
        self.return_block = func.append_basic_block('return')
    # enter the function scope
        self.var_stack.append(dict(self.var_stack[-1]))
        
        self.builder = Builder.new(entry)
    # create argument allocas
        if return_type != Type.void():
            self.ret_val = self.builder.alloca(return_type, None, 'ret_val')
        for arg, arg_decl in zip(func.args, funcNode.args.decl_list):
            arg.name = arg_decl.name
            alloca = self.builder.alloca(arg_decl.kind.llvm_pass_type(), None, arg_decl.name + '_content')
            self.builder.store(arg, alloca)
            self.var_stack[-1][arg_decl.name] = (alloca, arg_decl.kind.llvm_ref_type())
    # implement the function node
        self.funcImplLLVM(func, funcNode.impl)
    
    # implement the return basic block
        if self.builder.basic_block.terminator == None:
            self.builder.branch(self.return_block)
        
        self.builder.position_at_end(self.return_block)
        if return_type != Type.void():
            ret_val = self.builder.load(self.ret_val, 'ret_val')
            self.builder.ret(ret_val)
        else:
            self.builder.ret_void()
    # leave the function scope
        self.var_stack.pop()

    def funcImplLLVM(self, func, implNode):
        self.varDeclsLLVM(func, implNode.vars)
        self.statsLLVM(func, implNode.stats)
    
    def varDeclsLLVM(self, func, varDecls):
        for name, varDecl in varDecls.items():
            alloca = self.builder.alloca(varDecl.kind.llvm_type(), None, name)
            if varDecl.kind.llvm_ref_type() == 'pointer':
                ptr_ref = self.builder.alloca(Type.pointer(varDecl.kind.llvm_type()), None, varDecl.name)
                self.builder.store(alloca, ptr_ref)
                alloca = ptr_ref

            self.var_stack[-1][varDecl.name] = (alloca, varDecl.kind.llvm_ref_type())
    
    def statsLLVM(self, func, stats):
        for stat in stats:
            if isinstance(stat, AssignStat):
                self.assignStatLLVM(func, stat)
            elif isinstance(stat, ReturnStat):
                self.returnStatLLVM(func, stat)
                return 
                # ret belong to block terminator
                # one basic block only have on terminator
            elif isinstance(stat, PrintStat):
                self.printStatLLVM(func, stat)
            elif isinstance(stat, ExprStat):
                self.exprStatLLVM(stat.expr)
            elif isinstance(stat, IfStat):
                self.ifStatLLVM(func, stat)
            elif isinstance(stat, WhileStat):
                self.whileStatLLVM(func, stat)
            elif isinstance(stat, RepeatStat):
                self.repeatStatLLVM(func, stat)
            elif isinstance(stat, ForeachStat):
                self.foreachStatLLVM(func, stat)
            else:
                print("unsupported stats:{0}".format(type(stat)))
                raise Exception()

    def assignStatLLVM(self, func, assignStat):
        var_addr = self.getExprAddr(assignStat.lhs)
        result = self.exprStatLLVM(assignStat.rhs)
        self.builder.store(result, var_addr)

    def getExprAddr(self, addrExpr):
        if isinstance(addrExpr, VarRef):
            if addrExpr.name in self.var_stack[-1]:
                if self.var_stack[-1][addrExpr.name][1] == 'pointer':
                    result = self.builder.load(self.var_stack[-1][addrExpr.name][0], 'load_ptr')
                else:
                    result = self.var_stack[-1][addrExpr.name][0]
                return result
            else:
                print("No such variable {0}".format(addrExpr.name))
        elif isinstance(addrExpr, BracketExpr):
            array_ptr = self.getExprAddr(addrExpr.expr)
            result = self.builder.gep(array_ptr, [Constant.int(Type.int(32), 0), self.exprStatLLVM(addrExpr.index)], 'array_gep')
            return result
        elif isinstance(addrExpr, DotExpr):
            class_name = addrExpr.expr.kind.name
            index = self.kind_stack[-1][class_name][addrExpr.member]
            class_ptr = self.getExprAddr(addrExpr.expr)
            result = self.builder.gep(class_ptr, [Constant.int(Type.int(32), 0), Constant.int(Type.int(32), index)], 'class_member_gep')
            return result
        else:
            raise Exception()


    def returnStatLLVM(self, func, returnStat):
        if returnStat.expr != None:
            result = self.exprStatLLVM(returnStat.expr)
            self.builder.store(result, self.ret_val)
        
        self.builder.branch(self.return_block)

    def printStatLLVM(self, func, printStat):
        print_int = self.builder.call(self.print_int, [self.format_str, self.exprStatLLVM(printStat.expr)], "print_int")

    def exprStatLLVM(self, expr):
        if isinstance(expr, UnaryExpr):
            return self.unaryExprLLVM(expr)
        elif isinstance(expr, BinaryExpr):
            return self.binaryExprLLVM(expr)
        elif isinstance(expr, DotExpr):
            return self.dotExprLLVM(expr)
        elif isinstance(expr, BracketExpr):
            return self.bracketExprLLVM(expr)
        elif isinstance(expr, CallExpr):
            return self.callExprLLVM(expr)
        elif isinstance(expr, MethodExpr):
            return self.methodExprLLVM(expr)
        elif isinstance(expr, (BoolLiteral, NumLiteral)):
            return expr.llvm_value
        elif isinstance(expr, VarRef):
            return self.varRefLLVM(expr)
        else:
            print('no such expression' + str(type(expr)))
            raise Exception()

    def unaryExprLLVM(self, unaryExpr):
        expr = self.exprStatLLVM(unaryExpr.expr)
        
        if unaryExpr.op == "not":
            result = self.builder.icmp(ICMP_EQ, expr, Constant.int(expr.type, 0), "not_expr")
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
            lhs_bool = self.builder.icmp(ICMP_NE, lhs, Constant.int(lhs.type, 0), "lhs_bool")
            rhs_bool = self.builder.icmp(ICMP_NE, rhs, Constant.int(rhs.type, 0), "rhs_bool")
            result = self.builder.and_(lhs_bool, rhs_bool, "and_expr")
        elif binaryExpr.op == "or":
            lhs_bool = self.builder.icmp(ICMP_NE, lhs, Constant.int(lhs.type, 0), "lhs_bool")
            rhs_bool = self.builder.icmp(ICMP_NE, rhs, Constant.int(rhs.type, 0), "rhs_bool")
            result = self.builder.or_(lhs_bool, rhs_bool, "or_expr")
        else:
            print("no such operand {0}".format(binaryExpr.op))
            raise Exception()

        return result;

    def dotExprLLVM(self, dotExpr):
        member_ptr = self.getExprAddr(dotExpr)
        result = self.builder.load(member_ptr, 'member_extract')
        return result

    def bracketExprLLVM(self, bracketExpr):
        array_idx = self.getExprAddr(bracketExpr)
        result = self.builder.load(array_idx, 'array_extract')
        return result
    
    def callExprLLVM(self, callExpr):
        if isinstance(callExpr.expr, MethodExpr):
            method_name = callExpr.expr.klass.name + "::" + callExpr.expr.method.name
            callee = self.llvm_module.get_function_named(method_name)
        else:
            callee = self.llvm_module.get_function_named(callExpr.expr.name)
        arg_exprs = [ self.exprStatLLVM(arg) for arg in callExpr.args ]
        result = self.builder.call(callee, arg_exprs)
        return result

    def methodExprLLVM(self, methodEpxr):
        return Constant.int(Type.int(32), 1)

    def varRefLLVM(self, varRef):
        if varRef.name in self.var_stack[-1]:
            var_addr = self.var_stack[-1][varRef.name][0]
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
        result = self.builder.icmp(ICMP_NE, result, Constant.int(result.type, 0), "if_bool")
        if len(ifBranches) == 0:
            self.builder.cbranch(result, then_block, end_block)
        elif len(ifBranches) == 1:
            self.builder.cbranch(result, then_block, ifBranches[0][1])
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
                result = self.builder.icmp(ICMP_NE, result, Constant.int(result.type, 0), "if_bool")
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
        result = self.builder.icmp(ICMP_NE, result, Constant.int(result.type, 0), "while_bool")
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
        result = self.builder.icmp(ICMP_NE, result, Constant.int(result.type, 0), "repeat_bool")
        self.builder.cbranch(result, end_block, repeat_block)

        self.builder.position_at_end(end_block)

    def foreachStatLLVM(self, func, foreachStat):
    #build blocks
        foreach_block = func.append_basic_block("foreach")
        loop_block = func.append_basic_block("loop")
        end_block = func.append_basic_block("end_block")
    #implement
        temp_addr = self.builder.alloca(Type.int(32), None, "index_temp")
        self.builder.store(Constant.int(Type.int(32), 0), temp_addr)
        
        self.builder.branch(foreach_block)
        self.builder.position_at_end(foreach_block)
        temp_value = self.builder.load(temp_addr, "index_temp")
        if isinstance(foreachStat.expr.var.kind, ArrayKind):
            array_size = Constant.int(Type.int(32), foreachStat.expr.var.kind.size)
        else:
            print('only array support foreach statement')
            raise Exception()
        loop_expr = self.builder.icmp(ICMP_SLT, temp_value, array_size, 'cmp_result')
        self.builder.cbranch(loop_expr, loop_block, end_block)

        self.builder.position_at_end(loop_block)
        iter_var_addr = self.getExprAddr(foreachStat.var)
        array_ptr = self.getExprAddr(foreachStat.expr)
        array_gep = self.builder.gep(array_ptr, [Constant.int(Type.int(32), 0), temp_value], 'array_gep')
        array_value = self.builder.load(array_gep, 'array_value')
        self.builder.store(array_value, iter_var_addr)
        
        self.statsLLVM(func, foreachStat.stats)
        add_result = self.builder.add(temp_value, Constant.int(Type.int(32), 1),'add_result')
        self.builder.store(add_result, temp_addr)
        self.builder.branch(foreach_block)

        self.builder.position_at_end(end_block)

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
