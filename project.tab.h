/* A Bison parser, made by GNU Bison 3.0.2.  */

/* Bison interface for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2013 Free Software Foundation, Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

#ifndef YY_YY_PROJECT_TAB_H_INCLUDED
# define YY_YY_PROJECT_TAB_H_INCLUDED
/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 1
#endif
#if YYDEBUG
extern int yydebug;
#endif

/* Token type.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    K_PROGRAM = 258,
    K_FUNCTION = 259,
    K_TYPE = 260,
    K_VAR = 261,
    K_IS = 262,
    K_RETURN = 263,
    K_BEGIN = 264,
    K_IF = 265,
    K_THEN = 266,
    K_END = 267,
    K_ELIF = 268,
    K_ELSE = 269,
    K_WHILE = 270,
    K_DO = 271,
    K_REPEAT = 272,
    K_UNTIL = 273,
    K_FOREACH = 274,
    K_PRINT = 275,
    K_OF = 276,
    K_IN = 277,
    K_AND = 278,
    K_OR = 279,
    K_NOT = 280,
    K_ARRAY = 281,
    K_CLASS = 282,
    K_EXTENDS = 283,
    L_NUMBER = 284,
    L_YES = 285,
    L_NO = 286,
    IDENT = 287,
    P_SIMI = 288,
    P_DOT = 289,
    P_COMMA = 290,
    P_L_PARA = 291,
    P_R_PARA = 292,
    P_EQ = 293,
    P_LT = 294,
    P_LE = 295,
    P_GT = 296,
    P_GE = 297,
    P_NE = 298,
    P_ASSIGN = 299,
    P_L_BRACKET = 300,
    P_R_BRACKET = 301,
    P_ADD = 302,
    P_SUB = 303,
    P_MUL = 304,
    P_DIV = 305,
    P_MOD = 306,
    __DEBUG__ = 307
  };
#endif

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
typedef int YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;

int yyparse (void);

#endif /* !YY_YY_PROJECT_TAB_H_INCLUDED  */
