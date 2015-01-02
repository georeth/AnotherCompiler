from llvm import *
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
    #declare the function
        func_type = Type.function(funcNode.kind.ret.llvm_type,
                funcNode.kind.arg_llvm_type())
        func = Function.new(self.llvm_module, func_type, funcNode.name)
        
    # enter the function scope
        self.var_stack.append(dict(self.var_stack[-1]))
        i = 0
        for name in funcNode.args.names:
            func.args[i].name = name
            self.var_stack[-1][name] = func.args[i]
            i = i + 1
    # implement the function node
        self.funcImplLLVM(func, funcNode.impl)

    # leave the function scope
        self.var_stack.pop()

    def funcImplLLVM(self, func, implNode):
        entry = func.append_basic_block('entry')
        self.varDeclsLLVM(func, implNode.vars)
        self.builder = Builder.new(entry)
        self.statsLLVM(func, implNode.stats)
    
    def varDeclsLLVM(self, func, varDecls):
        return

    def statsLLVM(self, func, stats):
        for stat in stats:
            if isinstance(stat, AssignStat):
                self.assignStatLLVM(func, stat)
            elif isinstance(stat, ReturnStat):
                self.returnStatLLVM(func, stat)
            elif isinstance(stat, PrintStat):
                self.printStatLLVM(func, stat)
            elif isinstance(stat, ExprStat):
                self.exprStatLLVM(func, stat)
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
        return

    def returnStatLLVM(self, func, returnStat):
        return

    def printStatLLVM(self, func, printStat):
        return

    def exprStatLLVM(self, func, exprStat):
        return Constant.int(Type.int(32), 1)
    
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
        result = self.exprStatLLVM(func, ifStat.expr)
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
                result = self.exprStatLLVM(func, ifBranch[2].expr)
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
        result = self.exprStatLLVM(func, whileStat.expr)
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
        result = self.exprStatLLVM(func, repeatStat.expr)
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
