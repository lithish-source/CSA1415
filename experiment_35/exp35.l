%{
#include <stdio.h>
int is_digit = 0;
%}

%option noyywrap

%%

^[0-9]+$    { is_digit = 1; }
.|\n        { /* ignore */ }

%%

int main() {
    printf("Enter input: ");
    yylex();
    if (is_digit)
        printf("Given input is a Digit/Number\n");
    else
        printf("Given input is NOT a Digit/Number\n");
    return 0;
}
