#!/usr/bin/python3
from ply.lex import lex

reserved = {
    #"__debug__" : "__DEBUG__",

    "program" : "K_PROGRAM",
    "function" : "K_FUNCTION",
    "type" : "K_TYPE",
    "var" : "K_VAR",
    "is" : "K_IS",     
    "return" : "K_RETURN", 
    "begin" : "K_BEGIN",  
    "if" : "K_IF",     
    "then" : "K_THEN",   
    "end" : "K_END",    
    "elif" : "K_ELIF",   
    "else" : "K_ELSE",   
    "while" : "K_WHILE",  
    "do" : "K_DO",     
    "repeat" : "K_REPEAT", 
    "until" : "K_UNTIL",  
    "foreach" : "K_FOREACH",
    "print" : "K_PRINT",  
    "of" : "K_OF",     
    "array" : "K_ARRAY",  
    "class" : "K_CLASS",  
    "extends" : "K_EXTENDS",
    "in" : "K_IN",     

    "and" : "K_AND",
    "or" : "K_OR",
    "not" : "K_NOT",

    "yes" : "L_YES",
    "no" : "L_NO",
}
tokens = [
    "P_SEMI", "P_DOT", "P_COMMA", "P_L_PARA", "P_R_PARA", "P_L_BRACKET",
    "P_R_BRACKET", "P_EQ", "P_LT", "P_LE", "P_GT", "P_GE", "P_NE",
    "P_ASSIGN", "P_ADD", "P_SUB", "P_MUL", "P_DIV", "P_MOD",

    "L_NUMBER",

    "IDENT",
] + list(reserved.values())

def t_L_NUMBER(t):
    "[0-9]+"
    t.value = int(t.value)
    return t

def t_IDENT(t):
    r"[_a-zA-Z][_a-zA-Z0-9]*"
    t.type = reserved.get(t.value, "IDENT")
    return t

def t_newline(t):
    r"\n+"                    
    t.lexer.lineno += t.value.count('\n')

def t_whitespace(t):
    r"[ \t]+"
    pass
def t_comment(t):
    r"\/\/.*"
    pass

t_P_SEMI        = r";"                 
t_P_DOT         = r"\."    
t_P_COMMA       = r","    
t_P_L_PARA      = r"\("    
t_P_R_PARA      = r"\)"    
t_P_L_BRACKET   = r"\["    
t_P_R_BRACKET   = r"\]"    
t_P_EQ          = r"=="   
t_P_LT          = r"<"    
t_P_LE          = r"<="   
t_P_GT          = r">"    
t_P_GE          = r">="   
t_P_NE          = r"!="   
t_P_ASSIGN      = r":="   
t_P_ADD         = r"\+"     
t_P_SUB         = r"-"     
t_P_MUL         = r"\*"     
t_P_DIV         = r"/"     
t_P_MOD         = r"%"     

def t_error(t):
    print("Illegal str {0:.10s}".format(t.value))
    t.lexer.skip(1)

lexer = lex()
