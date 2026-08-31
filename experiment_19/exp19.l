%{
#include <stdio.h>
int char_count = 0;
int word_count = 0;
int line_count = 0;
%}

%option noyywrap

%%

"/*"([^*]|\*+[^*/])*\*+"/"    { /* Ignore block comments */ }
"//".*                        { /* Ignore line comments */ }
[ \t\r]+                      { /* Ignore redundant spaces and tabs */ }
\n                            { line_count++; }
[a-zA-Z_][a-zA-Z0-9_]*        { word_count++; char_count += yyleng; }
[0-9]+(\.[0-9]+)?             { word_count++; char_count += yyleng; }
.                             { char_count++; }

%%

int main(int argc, char **argv) {
    if (argc > 1) {
        FILE *file = fopen(argv[1], "r");
        if (!file) {
            perror("Error opening file");
            return 1;
        }
        yyin = file;
    }
    yylex();
    printf("Number of Characters: %d\n", char_count);
    printf("Number of Words: %d\n", word_count);
    printf("Number of Lines: %d\n", line_count);
    return 0;
}
