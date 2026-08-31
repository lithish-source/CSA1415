%{
#include <stdio.h>
int line_num = 1;
int is_start = 1;
%}

%option noyywrap

%%

\n     { putchar('\n'); is_start = 1; }
.      { 
         if (is_start) {
             printf("%d: ", line_num++);
             is_start = 0;
         }
         putchar(yytext[0]);
       }

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
