%{
#include <stdio.h>
int comment_count = 0;
FILE *out_fp;
%}

%option noyywrap

%%

"/*"([^*]|\*+[^*/])*\*+"/"    { comment_count++; }
"//".*                        { comment_count++; }
.|\n                          { fputs(yytext, out_fp); }

%%

int main(int argc, char **argv) {
    if (argc > 1) {
        FILE *fp = fopen(argv[1], "r");
        if (!fp) {
            perror("Error opening input file");
            return 1;
        }
        yyin = fp;
    }
    out_fp = fopen("output.c", "w");
    if (!out_fp) {
        perror("Error opening output file");
        return 1;
    }
    yylex();
    fclose(out_fp);
    printf("Total comment lines eliminated: %d\n", comment_count);
    return 0;
}
