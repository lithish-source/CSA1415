%{
#include <stdio.h>
%}

%option noyywrap

%%

auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|inline|int|long|register|restrict|return|short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while|_Bool|_Complex|_Imaginary { printf("Keyword: %s\n", yytext); }
[a-zA-Z_][a-zA-Z0-9_]*                                                                                                                                                                                                              { printf("Identifier: %s\n", yytext); }
.|\n                                                                                                                                                                                                                                { /* ignore other characters */ }

%%

int main() {
    printf("Enter input code/text: ");
    yylex();
    return 0;
}
