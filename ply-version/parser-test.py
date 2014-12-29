#!/usr/bin/python3
from lexer import lexer
from parser import parser
from syntax_tree import *
from syntax_tree_print import *
from analyze import *
from utils import for_each_file_do

def process(content, filename):
    prog = parser.parse(content)
    if prog:
        prog.visit(AnalyzeVisitor())
        prog.visit(PrintVisitor())

if __name__ == '__main__':
    for_each_file_do(process)
