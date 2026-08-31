%{
#include <stdio.h>
int valid = 0;
%}

%option noyywrap

%%

(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[012])\/(19[0-9]{2}|20[0-9]{2})    { valid = 1; }
(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[012])-(19[0-9]{2}|20[0-9]{2})    { valid = 1; }
.|\n                                                                { /* ignore */ }

%%

int main() {
    printf("Enter Date of Birth (DD/MM/YYYY or DD-MM-YYYY): ");
    yylex();
    if (valid)
        printf("Valid Date of Birth\n");
    else
        printf("Invalid Date of Birth\n");
    return 0;
}
