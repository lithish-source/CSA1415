%{
#include <stdio.h>
%}

%option noyywrap

%%

abc    { printf("ABC"); }
.|\n   { putchar(yytext[0]); }

%%

int main() {
    printf("Enter input string: ");
    yylex();
    return 0;
}
