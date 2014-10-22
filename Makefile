all: yacc lex
	gcc lex.yy.c project.tab.c -o project
lex: project.l
	flex project.l
lex-prog: lex
	gcc lex.yy.c -lfl -o lex-prog

yacc: project.y
	bison -d project.y --debug
