%{
#include <stdio.h>
int valid = 0;
%}

%option noyywrap

%%

[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}    { valid = 1; }
.|\n                                              { /* ignore */ }

%%

int main() {
    printf("Enter email address: ");
    yylex();
    if (valid)
        printf("Valid Email Address\n");
    else
        printf("Invalid Email Address\n");
    return 0;
}
