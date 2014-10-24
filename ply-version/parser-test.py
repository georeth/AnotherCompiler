#!/usr/bin/python3
from lexer import lexer
from parser import parser

s = []
while True:
    try:
        s.append(input())
    except:
        break

parser.parse('\n'.join(s))
