%{
#include <stdio.h>
int tag_count = 0;
%}

%option noyywrap

%%

"<"[^>]+">"    { printf("HTML Tag: %s\n", yytext); tag_count++; }
.|\n           { /* ignore text outside tags */ }

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
    printf("\nTotal HTML Tags found: %d\n", tag_count);
    return 0;
}
