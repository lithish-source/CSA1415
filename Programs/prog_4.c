#include <stdio.h>

int main() {
    char op;

    printf("Enter an operator: ");
    scanf("%c", &op);

    switch(op) {
        case '+':
            printf("'%c' is Addition Operator.\n", op);
            break;

        case '-':
            printf("'%c' is Subtraction Operator.\n", op);
            break;

        case '*':
            printf("'%c' is Multiplication Operator.\n", op);
            break;

        case '/':
            printf("'%c' is Division Operator.\n", op);
            break;

        default:
            printf("'%c' is Not an Arithmetic Operator.\n", op);
    }

    return 0;
}