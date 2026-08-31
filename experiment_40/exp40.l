%{
#include <stdio.h>
%}

%option noyywrap

%%

"#include"[ ]*"<"[^>]+">"                               { printf("[HEADER FILE]        : %s\n", yytext); }
int|float|void|char|double|return|main                  { printf("[KEYWORD]            : %s\n", yytext); }
[a-zA-Z_][a-zA-Z0-9_]*                                  { printf("[IDENTIFIER]         : %s\n", yytext); }
[0-9]+(\.[0-9]+)?                                       { printf("[CONSTANT]           : %s\n", yytext); }
\"[^\"]*\"                                              { printf("[STRING LITERAL]     : %s\n", yytext); }
"="|"+"|"-"|"*"|"/"                                     { printf("[OPERATOR]           : %s\n", yytext); }
"{"|"}"|"("|")"|";"|","                                 { printf("[DELIMITER/PUNCT]    : %s\n", yytext); }
[ \t\n]+                                                { /* ignore whitespace */ }
.                                                       { printf("[UNKNOWN TOKEN]      : %s\n", yytext); }

%%

int main(int argc, char **argv) {
    if (argc > 1) {
        FILE *fp = fopen(argv[1], "r");
        if (!fp) {
            perror("Error opening C source file");
            return 1;
        }
        yyin = fp;
    }
    printf("=== FLEX TOKEN SEPARATION RESULTS ===\n\n");
    yylex();
    return 0;
}
