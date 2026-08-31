#include <stdio.h>
#include <string.h>

/*
 Compiler Back End Implementation:
 Converts 3-address statements into machine-level target assembly instructions.
 Input:  t1 = a + b
 Output: MOV R0, a
         ADD R0, b
         MOV t1, R0
*/

int main() {
    char stmt[100];
    char res[10], op1[10], op2[10], oper;

    printf("Compiler Back End Code Generator\n");
    printf("--------------------------------\n");
    printf("Enter 3-address code statement (e.g. t1 = a + b): ");
    if (fgets(stmt, sizeof(stmt), stdin) == NULL) return 1;

    if (sscanf(stmt, "%s = %s %c %s", res, op1, &oper, op2) == 4) {
        printf("\nTarget Assembly Code Generated:\n");
        printf("-------------------------------\n");
        printf("MOV R0, %s\n", op1);
        switch (oper) {
            case '+': printf("ADD R0, %s\n", op2); break;
            case '-': printf("SUB R0, %s\n", op2); break;
            case '*': printf("MUL R0, %s\n", op2); break;
            case '/': printf("DIV R0, %s\n", op2); break;
            default:  printf("UNKNOWN OPERATOR\n"); break;
        }
        printf("MOV %s, R0\n", res);
    } else if (sscanf(stmt, "%s = %s", res, op1) == 2) {
        printf("\nTarget Assembly Code Generated:\n");
        printf("-------------------------------\n");
        printf("MOV R0, %s\n", op1);
        printf("MOV %s, R0\n", res);
    } else {
        printf("Invalid 3-address statement format.\n");
    }

    return 0;
}
