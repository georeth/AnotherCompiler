#!/usr/bin/python3
from lexer import lexer
from parser import parser
from syntax_tree import *
from syntax_tree_print import *
from analyze import *
from llvm_gen import *
from utils import for_each_file_do

def process(content, filename):
    prog = parser.parse(content)
    if prog:
        prog = analyze(prog)
        prog = prog.visit(PrintVisitor())
        llvm_gen = LLVMGenerator()
        llvm_gen.progLLVM(prog)

if __name__ == '__main__':
    for_each_file_do(process)
