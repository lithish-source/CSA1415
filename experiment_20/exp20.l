%{
#include <stdio.h>
int const_count = 0;
%}

%option noyywrap

%%

\"[^\"]*\"                    { printf("String Constant: %s\n", yytext); const_count++; }
[0-9]+\.[0-9]+                { printf("Floating Point Constant: %s\n", yytext); const_count++; }
[0-9]+                        { printf("Integer Constant: %s\n", yytext); const_count++; }
.|\n                          { /* ignore non-constants */ }

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
    printf("\nTotal Constants found: %d\n", const_count);
    return 0;
}
