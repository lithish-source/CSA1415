%{
#include <stdio.h>
#include <string.h>

char target_word[100];
char replace_word[100];
FILE *out_fp;
%}

%option noyywrap

%%

[a-zA-Z0-9_]+    {
                    if (strcmp(yytext, target_word) == 0)
                        fputs(replace_word, out_fp);
                    else
                        fputs(yytext, out_fp);
                 }
.|\n             { fputc(yytext[0], out_fp); }

%%

int main(int argc, char **argv) {
    if (argc < 4) {
        printf("Usage: %s <input_file> <target_word> <replacement_word>\n", argv[0]);
        return 1;
    }
    FILE *fp = fopen(argv[1], "r");
    if (!fp) {
        perror("Error opening input file");
        return 1;
    }
    yyin = fp;
    strcpy(target_word, argv[2]);
    strcpy(replace_word, argv[3]);
    
    out_fp = fopen("output.txt", "w");
    if (!out_fp) {
        perror("Error opening output file");
        return 1;
    }

    yylex();
    fclose(fp);
    fclose(out_fp);
    printf("Word replacement completed successfully in 'output.txt'\n");
    return 0;
}
