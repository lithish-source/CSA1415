#include <stdio.h>

int main()
{
    printf("Grammar:\n");
    printf("S -> AaAb | BbBa\n");
    printf("A -> ε\n");
    printf("B -> ε\n\n");

    printf("FIRST(A) = { ε }\n");
    printf("FIRST(B) = { ε }\n");
    printf("FIRST(S) = { a, b }\n");

    return 0;
}