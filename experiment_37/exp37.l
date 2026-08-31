%{
#include <stdio.h>
#include <string.h>

char target_word[100];
int count = 0;
%}

%option noyywrap

%%

[a-zA-Z0-9_]+    {
                    if (strcasecmp(yytext, target_word) == 0)
                        count++;
                 }
.|\n             { /* ignore punctuation and spaces */ }

%%

int main(int argc, char **argv) {
    if (argc > 1) {
        strcpy(target_word, argv[1]);
    } else {
        printf("Enter target word to search: ");
        if (scanf("%99s", target_word) != 1) return 1;
        // consume newline
        getchar();
    }
    printf("Enter sentence: ");
    yylex();
    printf("Frequency of '%s': %d\n", target_word, count);
    return 0;
}
