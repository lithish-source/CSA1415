#include <stdio.h>
#include <string.h>
#include <ctype.h>

/*
 Three Address Code (TAC) Generator
 Example expression: a = b + c * d
 Generates:
 t1 = c * d
 t2 = b + t1
 a = t2
*/

struct expr {
    char operand1[10];
    char operand2[10];
    char op;
    char result[10];
};

int main() {
    char input[100];
    printf("Enter infix assignment expression (e.g. a = b + c * d): ");
    if (fgets(input, sizeof(input), stdin) == NULL) return 1;

    char target[10], expr_str[100];
    if (sscanf(input, "%s = %[^\n]", target, expr_str) < 2) {
        printf("Invalid input format. Use: target = expr\n");
        return 1;
    }

    printf("\nThree Address Code Representation:\n");
    printf("----------------------------------\n");

    // Simple expression parser for basic binary operators (+, -, *, /)
    char op1[10], op2[10], op3[10];
    char oper1, oper2;

    int count = sscanf(expr_str, "%s %c %s %c %s", op1, &oper1, op2, &oper2, op3);

    if (count == 5) {
        // Checking operator precedence
        if ((oper2 == '*' || oper2 == '/') && (oper1 == '+' || oper1 == '-')) {
            printf("t1 = %s %c %s\n", op2, oper2, op3);
            printf("t2 = %s %c t1\n", op1, oper1);
            printf("%s = t2\n", target);
        } else {
            printf("t1 = %s %c %s\n", op1, oper1, op2);
            printf("t2 = t1 %c %s\n", oper2, op3);
            printf("%s = t2\n", target);
        }
    } else if (count == 3) {
        printf("t1 = %s %c %s\n", op1, oper1, op2);
        printf("%s = t1\n", target);
    } else {
        printf("%s = %s\n", target, expr_str);
    }

    return 0;
}
