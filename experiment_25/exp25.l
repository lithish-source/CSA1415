%{
#include <stdio.h>
%}

%option noyywrap

%%

[A-Z][a-zA-Z0-9]*    { printf("Capital Word: %s\n", yytext); }
.|\n                 { /* ignore non-capital words */ }

%%

int main() {
    printf("Enter input text: ");
    yylex();
    return 0;
}
