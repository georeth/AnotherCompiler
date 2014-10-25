#!/usr/bin/python3
import ply.yacc as yacc

from lexer import tokens

def p_program(p):
    "program :  K_PROGRAM IDENT argument_list   \
                    top_defs                    \
                K_IS                            \
                    variable_defs               \
                K_BEGIN                         \
                    statements                  \
                K_END                           "
    pass
def p_topdefs(p):
    """ top_defs :
                 | top_defs top_def """
    pass

def p_topdef(p):
    """ top_def : function_def
                | type_def
    """
    pass

def p_function_def(p):
    "function_def : K_FUNCTION IDENT argument_list \
                        variable_defs              \
                        return_type_opt            \
                    K_IS                           \
                        variable_defs              \
                    K_BEGIN                        \
                        statements                 \
                    K_END K_FUNCTION IDENT P_SEMI  "
    pass

def p_return_type_opt(p):
    """ return_type_opt :
                        | K_RETURN IDENT P_SEMI """
    pass

def p_type_def(p):
    """ type_def : class_def
                 | array_def """

def p_array_def(p):
    """ array_def : K_TYPE IDENT K_IS K_ARRAY K_OF L_NUMBER IDENT P_SEMI """

def p_class_def(p):
    "class_def :                                \
        K_TYPE IDENT K_IS K_CLASS extends_opt   \
            member_defs                         \
        K_END K_CLASS P_SEMI                    "
    pass

def p_extends_opt(p):
    """ extends_opt :
                    | K_EXTENDS IDENT """
    pass

def p_member_defs(p):
    """ member_defs :
                    | member_defs member_def """
    pass
def p_member_def(p):
    """ member_def : function_def
                   | variable_def """
    pass
def p_variable_defs(p):
    """ variable_defs :
                      | variable_defs variable_def """
    pass
def p_variable_def(p):
    """ variable_def : K_VAR IDENT K_IS IDENT P_SEMI """
    pass

def p_argument_list(p):
    """ argument_list : P_L_PARA arguments_opt P_R_PARA """
    pass

def p_arguments_opt(p):
    """ arguments_opt :
                      | arguments """
    pass

def p_arguments(p):
    """ arguments : IDENT
                  | arguments P_COMMA IDENT """
    pass

def p_rel_op(p):
    """ rel_op : P_LT
               | P_LE
               | P_EQ
               | P_NE
               | P_GT
               | P_GE """
    pass

def p_expr(p):
    """ expr : bool_term
             | expr K_OR bool_term """
    pass
def p_bool_term(p):
    """ bool_term : bool_factor
                  | bool_term K_AND bool_factor """
    pass

def p_bool_factor(p):
    """ bool_factor : bool_atom
                    | K_NOT bool_factor
    """
    pass
def p_bool_atom(p):
    """ bool_atom : L_YES
                  | L_NO
                  | arith_expr
                  | arith_expr rel_op arith_expr """
    pass


def p_arith_expr(p):
    """ arith_expr : arith_term_signed
                   | arith_expr P_ADD arith_term_signed
                   | arith_expr P_SUB arith_term_signed """
    pass

def p_arith_term_signed(p):
    """
    arith_term_signed : arith_term
                      | P_ADD arith_term_signed
                      | P_SUB arith_term_signed """
    pass
def p_arith_term(p):
    """
    arith_term : arith_factor
               | arith_term P_MUL arith_factor
               | arith_term P_DIV arith_factor
               | arith_term P_MOD arith_factor """
    pass

def p_arith_factor(p):
    """
    arith_factor : arith_atom
                 | arith_factor P_DOT IDENT
                 | arith_factor P_DOT IDENT pass_value_list
                 | arith_factor P_L_BRACKET expr P_R_BRACKET
    """
    pass

def p_arith_atom(p):
    """
    arith_atom : L_NUMBER
               | P_L_PARA expr P_R_PARA
               | IDENT pass_value_list
               | IDENT
    """
    pass

def p_pass_value_list(p):
    """
    pass_value_list : P_L_PARA pass_values_opt P_R_PARA
    """
    pass

def p_pass_values_opt(p):
    """
    pass_values_opt :
                    | pass_values
    """
    pass
def p_pass_values(p):
    """
    pass_values : expr
                | pass_values P_COMMA expr
    """
    pass


def p_statements(p):
    """
    statements :
               | statements statement
    """
    pass
def p_statement(p):
    """
    statement : assign_stat
              | if_stat
              | while_stat
              | repeat_stat
              | foreach_stat
              | return_stat
              | print_stat
              | expr P_SEMI
    """
    pass

def p_assign_stat(p):
    """
    assign_stat : expr P_ASSIGN expr P_SEMI
    """
    pass
def p_if_stat(p):
    " if_stat : K_IF expr K_THEN  \
                    statements    \
                elif_branches     \
                else_branch_opt   \
                K_END K_IF        "
    pass
def p_elif_branches(p):
    """ elif_branches :
                      | elif_branches elif_branch
    """
    pass
def p_elif_branch(p):
    " elif_branch : K_ELIF expr K_THEN  \
                        statements      "
    pass
def p_else_branch_opt(p):
    """ else_branch_opt :
                        | K_ELSE statements """
    pass
def p_while_stat(p):
    " while_stat :                      \
              K_WHILE expr K_DO         \
                statements              \
              K_END K_WHILE             "
    pass

def p_repeat_stat(p):
    " repeat_stat :                 \
            K_REPEAT                \
                statements          \
            K_UNTIL expr P_SEMI     "
    pass

def p_foreach_stat(p):
    " foreach_stat :                    \
        K_FOREACH IDENT K_IN expr K_DO  \
            statements                  \
        K_END K_FOREACH                 "
    pass
def p_return_stat(p):
    """ return_stat : K_RETURN P_SEMI
                    | K_RETURN expr P_SEMI """
    if len(p) == 4:
        print("here1 " + str(p.slice[1].type))
        print("here2 " + str(p.slice[2].type))
    pass
def p_print_stat(p):
    """ print_stat : K_PRINT expr P_SEMI """
    pass

def p_error(tok):
    print("syntax error {0}".format(tok))

parser = yacc.yacc()
