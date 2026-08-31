#include <stdio.h>

int main()
{
    printf("Original Grammar:\n");
    printf("S -> (L) | a\n");
    printf("L -> L,S | S\n\n");

    printf("Grammar after eliminating Left Recursion:\n");
    printf("L -> SL'\n");
    printf("L' -> ,SL' | ε\n");

    return 0;
}