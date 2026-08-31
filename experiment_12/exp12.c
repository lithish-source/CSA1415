#include <stdio.h>
#include <string.h>
#include <stdlib.h>

/*
 Grammar:
 E  -> T E'
 E' -> + T E' | e
 T  -> F T'
 T' -> * F T' | e
 F  -> ( E ) | id
*/

char input[100];
int i = 0;

int E();
int EP();
int T();
int TP();
int F();

int F() {
    if (input[i] == '(') {
        i++;
        if (E()) {
            if (input[i] == ')') {
                i++;
                return 1;
            } else return 0;
        } else return 0;
    } else if ((input[i] >= 'a' && input[i] <= 'z') || (input[i] >= 'A' && input[i] <= 'Z')) {
        i++;
        // match remaining identifier alphanumeric chars if any
        while ((input[i] >= 'a' && input[i] <= 'z') || 
               (input[i] >= 'A' && input[i] <= 'Z') || 
               (input[i] >= '0' && input[i] <= '9')) {
            i++;
        }
        return 1;
    }
    return 0;
}

int TP() {
    if (input[i] == '*') {
        i++;
        if (F()) {
            if (TP()) return 1;
            else return 0;
        } else return 0;
    }
    return 1; // e (epsilon)
}

int T() {
    if (F()) {
        if (TP()) return 1;
        else return 0;
    }
    return 0;
}

int EP() {
    if (input[i] == '+') {
        i++;
        if (T()) {
            if (EP()) return 1;
            else return 0;
        } else return 0;
    }
    return 1; // e (epsilon)
}

int E() {
    if (T()) {
        if (EP()) return 1;
        else return 0;
    }
    return 0;
}

int main() {
    printf("Recursive Descent Parser for Grammar:\n");
    printf("E  -> T E'\n");
    printf("E' -> + T E' | e\n");
    printf("T  -> F T'\n");
    printf("T' -> * F T' | e\n");
    printf("F  -> ( E ) | id\n\n");
    
    printf("Enter the input string: ");
    if (scanf("%99s", input) != 1) return 1;
    
    if (E() && input[i] == '\0') {
        printf("String is SUCCESSFULLY parsed! (Valid input)\n");
    } else {
        printf("String Parsing FAILED! (Invalid input)\n");
    }
    return 0;
}
