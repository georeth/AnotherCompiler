#!/usr/bin/python3
from lexer import lexer

s = []
while True:
    try:
        s.append(input())
    except:
        break
lexer.input('\n'.join(s))
# Tokenize
for tok in lexer:
    print (tok)
