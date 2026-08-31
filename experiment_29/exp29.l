%{
#include <stdio.h>
%}

%option noyywrap

%%

"#include"[ ]*"<"[^>]+">"                               { printf("Header File: %s\n", yytext); }
int|float|void|char|double|return|main                  { printf("Keyword: %s\n", yytext); }
[a-zA-Z_][a-zA-Z0-9_]*                                  { printf("Identifier: %s\n", yytext); }
[0-9]+(\.[0-9]+)?                                       { printf("Constant: %s\n", yytext); }
\"[^\"]*\"                                              { printf("String Literal: %s\n", yytext); }
"="|"+"|"-"|"*"|"/"                                     { printf("Operator: %s\n", yytext); }
"{"|"}"|"("|")"|";"|","                                 { printf("Punctuation/Separator: %s\n", yytext); }
[ \t\n]+                                                { /* ignore whitespace */ }
.                                                       { printf("Unknown Token: %s\n", yytext); }

%%

int main(int argc, char **argv) {
    if (argc > 1) {
        FILE *fp = fopen(argv[1], "r");
        if (!fp) {
            perror("Error opening file");
            return 1;
        }
        yyin = fp;
    }
    yylex();
    return 0;
}
