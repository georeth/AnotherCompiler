#!/usr/bin/python3
from lexer import lexer
from utils import for_each_file_do

def process(content, filename):
    lexer.input(content)
    # Tokenize
    for tok in lexer:
        print (tok)

if __name__ == '__main__':
    for_each_file_do(process)
