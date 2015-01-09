#!/usr/bin/python3
import argparse
import fileinput

from lexer import lexer
from parser import parser
from syntax_tree import *
from syntax_tree_print import *
from analyze import *
from llvm_gen import *
from utils import for_each_file_do

def for_each_file_do(files, process):
    filename = None
    content = ''
    for line in fileinput.input(files):
        if fileinput.filename() != filename:
            if filename is not None:
                process(content, filename)
            content = ''
            filename = fileinput.filename()
        content += line
    if content:
        process(content, filename)

def mylang_lex(content, filename):
    lexer.input(content)
    # Tokenize
    for tok in lexer:
        print (tok)

def mylang_compile(content, filename, mode='compile'):
    prog = parser.parse(content)
    if not prog: return
    if mode == 'analyze' or mode == 'compile':
        prog = analyze(prog)
    if mode != 'compile':
        prog.visit(PrintVisitor())
    else:
        llvm_gen = LLVMGenerator()
        llvm_gen.progLLVM(prog)

def main():
    parser = argparse.ArgumentParser(description="MyLang Compiler")
    group = parser.add_mutually_exclusive_group()

    group.add_argument("-l", "--lex", action="store_true",
            help="Run the lex step only, printing lex tokens.")
    group.add_argument("-p", "--parse", action="store_true",
            help="Run the parse step only, printing the parse tree.")
    group.add_argument("-a", "--analyze", action="store_true",
            help="Analyze the program syntax tree without code generation.")
    group.add_argument("-c", "--compile", action="store_true", default=True,
            help="Run the full compilation steps (default running mode).")

    parser.add_argument("sources", metavar='file', nargs='*',
            help="MyLang source files (if empty, read from stdin).")
    args = parser.parse_args()

    files = args.sources

    if args.lex:
        for_each_file_do(files, mylang_lex)
        return

    mode = 'compile'
    if args.parse:
        mode = 'parse'
    elif args.analyze:
        mode = 'analyze'

    def do_compile(content, filename):
        mylang_compile(content, filename, mode)
    for_each_file_do(files, do_compile)

if __name__ == '__main__':
    main()
