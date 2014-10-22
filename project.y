%{
#include <stdio.h>
void yyerror(const char *str){
    fprintf(stderr,"error: %s\n",str);
}
int yywrap()
{
    return 1;
} 
int main()
{
    yyparse();
} 

%}
%token K_PROGRAM K_FUNCTION K_TYPE K_VAR K_IS K_RETURN K_BEGIN K_IF K_THEN K_END K_ELIF K_ELSE K_WHILE K_DO K_REPEAT K_UNTIL K_FOREACH K_PRINT K_OF K_IN /* KEYWORDS */
%token K_AND K_OR K_NOT
%token K_ARRAY K_CLASS K_EXTENDS /* TYPES */ /* integer boolean is not keyword */
%token L_NUMBER L_YES L_NO/* literal */
%token IDENT
%token P_SIMI P_DOT P_COMMA P_L_PARA P_R_PARA P_EQ P_LT P_LE P_GT P_GE P_NE P_ASSIGN P_L_BRACKET P_R_BRACKET P_ADD P_SUB P_MUL P_DIV P_MOD/* PUNCTURATIONS */

%% 

program:
    K_PROGRAM IDENT argument_list
        top_defs 
    K_IS 
        variable_defs 
    K_BEGIN 
        statements
    K_END;

top_defs:
        |
        top_def top_defs;

top_def:
    function_def | type_def;

function_def:
    K_FUNCTION IDENT argument_list
        variable_defs /* argument_defs */
        return_type_opt
    K_IS
        variable_defs
    K_BEGIN
        statements
    K_END K_FUNCTION IDENT P_SIMI;

return_type_opt:
               |
               K_RETURN IDENT P_SIMI;

type_def:
    class_def | array_def;
array_def:
    K_TYPE IDENT K_IS K_ARRAY K_OF L_NUMBER IDENT P_SIMI;
class_def:
    K_TYPE IDENT K_IS K_CLASS extends_opt
        member_defs
    K_END K_CLASS P_SIMI;
extends_opt:
           |
           K_EXTENDS IDENT;

member_defs:
           |
           member_def member_defs
           ;
member_def:
          function_def | variable_def; 
variable_defs: 
             |
             variable_def variable_defs;
variable_def: K_VAR IDENT K_IS IDENT P_SIMI;

argument_list: /* (a, b, c) */
    P_L_PARA arguments_opt P_R_PARA;
arguments_opt:
             | 
             arguments;

arguments: 
         IDENT 
         |
         IDENT P_COMMA IDENT;

expr: 
         bool_term {printf("1EXPR\n");}
         | 
         expr K_OR bool_term;
bool_term:
         bool_factor
      {printf("BOOL\n");}
         |
         bool_term {printf("ABC\n");} K_AND {printf("AND\n");} bool_factor;

bool_factor:
           bool_atom {printf("FACTOR\n");} | K_NOT bool_factor;
bool_atom:
         L_YES
         |
         L_NO
         | 
         arith_expr
      {printf("ATOM\n");}
         |
         arith_expr rel_op arith_expr;


arith_expr:
    arith_term
      {printf("ARITH_EXPR\n");}
    |
    arith_expr P_ADD arith_term
    |
    arith_expr P_SUB arith_term;
arith_term:
    P_ADD arith_term
    |
    P_SUB arith_term
    |
    arith_factor
    |
    arith_term P_MUL arith_factor
    |
    arith_term P_DIV arith_factor
    |
    arith_term P_MOD arith_factor;

arith_factor:
      L_NUMBER 
      | 
      lvalue /*HACK*/
      |
      P_L_PARA expr P_R_PARA
      |
      function_call
      ;

function_call:
      expr P_L_PARA pass_value_list P_R_PARA;

pass_value_list:
      |
      pass_values;

pass_values:
      expr
      |
      pass_values P_COMMA expr;

lvalue:
      IDENT {printf("ID\n");}
      |
      arith_factor subscript
      |
      arith_factor P_DOT IDENT;

subscript:
         P_L_BRACKET expr P_R_BRACKET;

rel_op:
      P_LT | P_LE | P_EQ | P_NE | P_GT | P_GE;

statements: 
         |
         statement statements;
statement:
         assign_stat
         |
         if_stat
         |
         while_stat
         |
         repeat_stat
         |
         foreach_stat
         |
         return_stat
         |
         print_stat
         | 
         expr P_SIMI; /* f() */

assign_stat: 
        lvalue P_ASSIGN expr P_SIMI;
if_stat:
       K_IF expr K_THEN
            statements
       elif_branches
       else_brach_opt
       K_END K_IF;
elif_branches:
             |
             elif_branch elif_branches;
elif_branch:
           K_ELIF expr K_THEN
                statements;
else_brach_opt:
              |
              K_ELSE 
                statements;
while_stat:
          K_WHILE expr K_DO
            statements
          K_END K_WHILE;
      
repeat_stat:
    K_REPEAT
        statements
    K_UNTIL expr P_SIMI;

foreach_stat:
    K_FOREACH IDENT K_IN expr K_DO
        statements
    K_END K_FOREACH;
return_stat:
    K_RETURN P_SIMI
    |
    K_RETURN expr P_SIMI;
print_stat:
    K_PRINT expr P_SIMI;
