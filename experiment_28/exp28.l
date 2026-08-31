%{
#include <stdio.h>
int valid = 0;
%}

%option noyywrap

%%

[6-9][0-9]{9}    { valid = 1; }
.|\n             { /* ignore */ }

%%

int main() {
    printf("Enter Mobile Number: ");
    yylex();
    if (valid)
        printf("Valid Mobile Number\n");
    else
        printf("Invalid Mobile Number\n");
    return 0;
}
