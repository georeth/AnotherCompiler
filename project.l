%{
#include <stdio.h>
#include "project.tab.h"
%}

%%
 

"__debug__"            return __DEBUG__;

program      return K_PROGRAM;
function      return K_FUNCTION;
type      return K_TYPE;
var      return K_VAR;
is      return K_IS;
return     return K_RETURN;
begin      return K_BEGIN;
if      return K_IF;
then      return K_THEN;
end      return K_END;
elif      return K_ELIF;
else      return K_ELSE;
while      return K_WHILE;
do      return K_DO;
repeat      return K_REPEAT;
until      return K_UNTIL;
foreach      return K_FOREACH;
print      return K_PRINT;
of      return K_OF;
array      return K_ARRAY;
class      return K_CLASS;
extends      return K_EXTENDS;
in            return K_IN;

and                    return K_AND;
or                    return K_OR;
not                    return K_NOT;

[0-9]+                  return L_NUMBER;
yes                     return L_YES;
no                      return L_NO;
[_a-zA-Z][_a-zA-Z0-9]*   return IDENT;
\n                      /* ignore end of line */;
[ \t]+                  /* ignore whitespace */;
\/\/.*                    /* ignore comments*/;

";"                     return P_SEMI;
"."                    return P_DOT;
","                    return P_COMMA;
"("                    return P_L_PARA;
")"                    return P_R_PARA;
"["                    return P_L_BRACKET;
"]"                    return P_R_BRACKET;
"=="                   return P_EQ;
"<"                     return P_LT;
"<="                   return P_LE;
">"                     return P_GT;
">="                   return P_GE;
"!="                   return P_NE;
":="                    return P_ASSIGN ;
"+"                    return P_ADD;
"-"                    return P_SUB;
"*"                    return P_MUL;
"/"                    return P_DIV;
"%"                    return P_MOD;

%%
