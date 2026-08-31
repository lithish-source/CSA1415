%{
#include <stdio.h>
int valid = 0;
%}

%option noyywrap

%%

(https?:\/\/)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(\/[a-zA-Z0-9#?&%=-]*)*    { valid = 1; }
.|\n                                                                           { /* ignore */ }

%%

int main() {
    printf("Enter URL: ");
    yylex();
    if (valid)
        printf("Valid URL\n");
    else
        printf("Invalid URL\n");
    return 0;
}
