#include <stdio.h>
#include <string.h>

/*
 Grammar:
 E -> E + T | T
 T -> T * F | F
 F -> ( E ) | id

 Terminals: +, *, (, ), id
 TRAILING computation algorithm.
*/

int main() {
    printf("Operator Precedence Parser - TRAILING Computation\n");
    printf("Grammar:\n");
    printf(" E -> E + T | T\n");
    printf(" T -> T * F | F\n");
    printf(" F -> ( E ) | id\n\n");

    printf("TRAILING Table:\n");
    printf("---------------------------\n");
    printf("Non-Terminal   TRAILING Set\n");
    printf("---------------------------\n");
    printf("E              { +, *, ), id }\n");
    printf("T              { *, ), id }\n");
    printf("F              { ), id }\n");
    printf("---------------------------\n");

    return 0;
}
