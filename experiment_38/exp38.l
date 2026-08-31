%{
#include <stdio.h>
#include <string.h>

int max_len = 0;
char longest_word[256] = "";
%}

%option noyywrap

%%

[a-zA-Z0-9_]+    {
                    if (yyleng > max_len) {
                        max_len = yyleng;
                        strcpy(longest_word, yytext);
                    }
                 }
.|\n             { /* ignore */ }

%%

int main() {
    printf("Enter sentence: ");
    yylex();
    printf("Longest Word: %s (Length: %d)\n", longest_word, max_len);
    return 0;
}
