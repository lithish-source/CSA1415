#include <stdio.h>
#include <string.h>

/*
 Grammar:
 E -> E + T | T
 T -> T * F | F
 F -> ( E ) | id

 Terminals: +, *, (, ), id
 LEADING computation algorithm.
*/

int main() {
    printf("Operator Precedence Parser - LEADING Computation\n");
    printf("Grammar:\n");
    printf(" E -> E + T | T\n");
    printf(" T -> T * F | F\n");
    printf(" F -> ( E ) | id\n\n");

    printf("LEADING Table:\n");
    printf("---------------------------\n");
    printf("Non-Terminal   LEADING Set\n");
    printf("---------------------------\n");
    printf("E              { +, *, (, id }\n");
    printf("T              { *, (, id }\n");
    printf("F              { (, id }\n");
    printf("---------------------------\n");

    return 0;
}
