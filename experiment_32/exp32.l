%{
#include <stdio.h>
int pos_count = 0;
int neg_count = 0;
%}

%option noyywrap

%%

\+?[0-9]+(\.[0-9]+)?    { printf("Positive Number: %s\n", yytext); pos_count++; }
-[0-9]+(\.[0-9]+)?     { printf("Negative Number: %s\n", yytext); neg_count++; }
[ \t\n]+                { /* ignore whitespace */ }
.                       { /* ignore others */ }

%%

int main() {
    printf("Enter numbers: ");
    yylex();
    printf("\nTotal Positive Numbers: %d\n", pos_count);
    printf("Total Negative Numbers: %d\n", neg_count);
    return 0;
}
