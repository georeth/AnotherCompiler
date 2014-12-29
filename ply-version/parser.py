#!/usr/bin/python3
import ply.yacc as yacc

from lexer import tokens
from syntax_tree import *

def p_program(p):
    "program :  K_PROGRAM IDENT argument_list   \
                    top_defs                    \
                K_IS                            \
                impl                            "
    p[0] = Program(p[2], p[3], p[4], p[6])

def p_topdefs(p):
    """ top_defs :
                 | top_defs top_def """
    if len(p) == 1:
        p[0] = {}
    else:
        defs = dict(p[1])
        defs[p[2].name] = p[2]
        p[0] = defs

def p_topdef(p):
    """ top_def : function_def
                | type_def
    """
    p[0] = p[1]

def p_function_def(p):
    "function_def : K_FUNCTION IDENT argument_list \
                        variable_defs              \
                        return_type_opt            \
                    K_IS                           \
                    impl                           \
                    K_FUNCTION IDENT P_SEMI        "
    p[0] = FuncDecl(p[2], ArgList(p[3], p[4]), p[5], p[7])

def p_impl(p):
    "impl : variable_defs                  \
            K_BEGIN                        \
                statements                 \
            K_END                          "
    p[0] = Impl(p[1], p[3])

def p_return_type_opt(p):
    """ return_type_opt :
                        | K_RETURN IDENT P_SEMI """
    if len(p) == 1:
        return None
    p[0] = KindRef(p[2])

def p_type_def(p):
    """ type_def : class_def
                 | array_def """
    p[0] = p[1]

def p_array_def(p):
    """ array_def : K_TYPE IDENT K_IS K_ARRAY K_OF L_NUMBER IDENT P_SEMI """
    p[0] = KindDecl(p[2], ArrayKind(int(p[6]), KindRef(p[7])))

def p_class_def(p):
    "class_def :                                \
        K_TYPE IDENT K_IS K_CLASS extends_opt   \
            member_defs                         \
        K_END K_CLASS P_SEMI                    "
    p[0] = KindDecl(p[2], Klass(p[6], p[5], p[2]))

def p_extends_opt(p):
    """ extends_opt :
                    | K_EXTENDS IDENT """
    if len(p) == 1:
        p[0] = None
    else:
        p[0] = KindRef(p[2])

def p_member_defs(p):
    """ member_defs :
                    | member_defs member_def """
    if len(p) == 1:
        p[0] = {}
    else:
        defs = dict(p[1])
        defs[p[2].name] = p[2]
        p[0] = defs

def p_member_def(p):
    """ member_def : function_def
                   | variable_def """
    p[0] = p[1]

def p_variable_defs(p):
    """ variable_defs :
                      | variable_defs variable_def """
    if len(p) == 1:
        p[0] = {}
    else:
        defs = dict(p[1])
        defs[p[2].name] = p[2]
        p[0] = defs

def p_variable_def(p):
    """ variable_def : K_VAR IDENT K_IS IDENT P_SEMI """
    p[0] = VarDecl(p[2], KindRef(p[4]))

def p_argument_list(p):
    """ argument_list : P_L_PARA arguments_opt P_R_PARA """
    p[0] = p[2]

def p_arguments_opt(p):
    """ arguments_opt :
                      | arguments """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]

def p_arguments(p):
    """ arguments : IDENT
                  | arguments P_COMMA IDENT """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        args = list(p[1])
        args.append(p[3])
        p[0] = args

def p_rel_op(p):
    """ rel_op : P_LT
               | P_LE
               | P_EQ
               | P_NE
               | P_GT
               | P_GE """
    p[0] = p[1]

def p_expr(p):
    """ expr : bool_term
             | expr K_OR bool_term """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryExpr(BoolKind.kind, p[1], "or", p[3])

def p_bool_term(p):
    """ bool_term : bool_factor
                  | bool_term K_AND bool_factor """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryExpr(BoolKind.kind, p[1], "and", p[3])

def p_bool_factor(p):
    """ bool_factor : bool_atom
                    | K_NOT bool_factor
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = UnaryExpr(BoolKind.kind, "not", p[2])

def p_bool_atom(p):
    """ bool_atom : bool_literal
                  | arith_expr
                  | arith_expr rel_op arith_expr """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryExpr(BoolKind.kind, p[1], p[2], p[3])

def p_bool_literal(p):
    """ bool_literal : L_YES
                     | L_NO """
    if p[1] == "yes":
        p[0] = YesLiteral()
    else:
        p[0] = NoLiteral()

def p_arith_expr(p):
    """ arith_expr : arith_term_signed
                   | arith_expr P_ADD arith_term_signed
                   | arith_expr P_SUB arith_term_signed """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryExpr(NumKind.kind, p[1], p[2], p[3])

def p_arith_term_signed(p):
    """
    arith_term_signed : arith_term
                      | P_ADD arith_term_signed
                      | P_SUB arith_term_signed """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = UnaryExpr(NumKind.kind, p[1], p[2])

def p_arith_term(p):
    """
    arith_term : arith_factor
               | arith_term P_MUL arith_factor
               | arith_term P_DIV arith_factor
               | arith_term P_MOD arith_factor """
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = BinaryExpr(NumKind.kind, p[1], p[2], p[3])

def p_arith_factor(p):
    """
    arith_factor : arith_atom
                 | arith_factor P_DOT IDENT
                 | arith_factor P_DOT IDENT pass_value_list
                 | arith_factor P_L_BRACKET expr P_R_BRACKET
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = DotExpr(None, p[1], p[3])
    elif len(p) == 5:
        if p[2] == '.':
            p[0] = CallExpr(DotExpr(None, p[1], p[3]), p[4], p[1])
        else:
            p[0] = BracketExpr(None, p[1], p[3])

def p_arith_atom(p):
    """
    arith_atom : num_literal
               | variable_ref
               | P_L_PARA expr P_R_PARA
               | IDENT pass_value_list
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = CallExpr(VarRef(p[1], None), p[2])
    elif len(p) == 4:
        p[0] = p[2]

def p_num_literal(p):
    """
    num_literal : L_NUMBER
    """
    # TODO(utf8please): Maybe allow float?
    p[0] = NumLiteral(int(p[1]))

def p_variable_ref(p):
    """
    variable_ref : IDENT
    """
    p[0] = VarRef(p[1], None)

def p_pass_value_list(p):
    """
    pass_value_list : P_L_PARA pass_values_opt P_R_PARA
    """
    p[0] = p[2]

def p_pass_values_opt(p):
    """
    pass_values_opt :
                    | pass_values
    """
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]

def p_pass_values(p):
    """
    pass_values : expr
                | pass_values P_COMMA expr
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        args = list(p[1])
        args.append(p[3])
        p[0] = args

def p_statements(p):
    """
    statements :
               | statements statement
    """
    if len(p) == 1:
        p[0] = []
    else:
        args = list(p[1])
        args.append(p[2])
        p[0] = args

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
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = ExprStat(p[1])

def p_assign_stat(p):
    """
    assign_stat : expr P_ASSIGN expr P_SEMI
    """
    p[0] = AssignStat(p[1], p[3])

def p_if_stat(p):
    " if_stat : K_IF expr K_THEN  \
                    statements    \
                elif_branches     \
                else_branch_opt   \
                K_END K_IF        "
    branches = list(p[5])
    if p[6]:
        branches.append(p[6])
    p[0] = IfStat(p[2], p[4], branches)

def p_elif_branches(p):
    """ elif_branches :
                      | elif_branches elif_branch
    """
    if len(p) == 1:
        p[0] = []
    else:
        args = list(p[1])
        args.append(p[2])
        p[0] = args

def p_elif_branch(p):
    " elif_branch : K_ELIF expr K_THEN  \
                        statements      "
    p[0] = IfBranch(p[2], p[4])

def p_else_branch_opt(p):
    """ else_branch_opt :
                        | K_ELSE statements """
    if len(p) == 1:
        p[0] = None
    else:
        p[0] = IfBranch(None, p[2])

def p_while_stat(p):
    " while_stat :                      \
              K_WHILE expr K_DO         \
                statements              \
              K_END K_WHILE             "
    p[0] = WhileStat(p[2], p[4])

def p_repeat_stat(p):
    " repeat_stat :                 \
            K_REPEAT                \
                statements          \
            K_UNTIL expr P_SEMI     "
    p[0] = RepeatStat(p[4], p[2])

def p_foreach_stat(p):
    " foreach_stat :                    \
        K_FOREACH IDENT K_IN expr K_DO  \
            statements                  \
        K_END K_FOREACH                 "
    p[0] = ForeachStat(VarRef(p[2], None), p[4], p[6])

def p_return_stat(p):
    """ return_stat : K_RETURN P_SEMI
                    | K_RETURN expr P_SEMI """
    if len(p) == 3:
        p[0] = ReturnStat(None)
    else:
        p[0] = ReturnStat(p[2])

def p_print_stat(p):
    """ print_stat : K_PRINT expr P_SEMI """
    p[0] = PrintStat(p[2])

def p_error(tok):
    print("syntax error {0}".format(tok))
    print("line :", tok.lexer.lineno);

parser = yacc.yacc()
