%{
#include <stdio.h>
#include <stdlib.h>

int op = 0;
float a = 0, b = 0;
void evaluate();
%}

%option noyywrap

dig [0-9]+(\.[0-9]+)?
add "+"
sub "-"
mul "*"
div "/"
pow "^"
ln \n

%%

{dig} {
    if (op == 0)
        a = atof(yytext);
    else
        b = atof(yytext);
}
{add} { op = 1; }
{sub} { op = 2; }
{mul} { op = 3; }
{div} { op = 4; }
{ln}  { evaluate(); }
.     { /* ignore spaces/other chars */ }

%%

void evaluate() {
    switch(op) {
        case 1: printf("Result: %.2f\n", a + b); break;
        case 2: printf("Result: %.2f\n", a - b); break;
        case 3: printf("Result: %.2f\n", a * b); break;
        case 4: 
            if (b != 0) printf("Result: %.2f\n", a / b);
            else printf("Error: Division by zero\n");
            break;
        default: printf("Result: %.2f\n", a); break;
    }
    op = 0;
}

int main() {
    printf("Enter basic mathematical operation (e.g. 15 + 25): ");
    yylex();
    return 0;
}
