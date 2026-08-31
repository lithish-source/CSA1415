#include <stdio.h>
#include <string.h>

/*
 Shift-Reduce Parser (Bottom-Up Parsing)
 Simple Grammar:
 E -> E + E
 E -> E * E
 E -> ( E )
 E -> id
*/

char input[100], stack[100];
int input_len, stack_ptr = 0, i = 0;

void print_step(char *action) {
    printf("%-20s %-20s %-20s\n", stack, input + i, action);
}

void check_reduce() {
    int reduced = 1;
    while (reduced) {
        reduced = 0;
        // Check E -> id
        if (stack_ptr >= 2 && stack[stack_ptr - 2] == 'i' && stack[stack_ptr - 1] == 'd') {
            stack[stack_ptr - 2] = 'E';
            stack[stack_ptr - 1] = '\0';
            stack_ptr -= 1;
            print_step("REDUCE E -> id");
            reduced = 1;
        }
        // Check E -> E + E
        else if (stack_ptr >= 3 && stack[stack_ptr - 3] == 'E' && stack[stack_ptr - 2] == '+' && stack[stack_ptr - 1] == 'E') {
            stack[stack_ptr - 3] = 'E';
            stack[stack_ptr - 2] = '\0';
            stack_ptr -= 2;
            print_step("REDUCE E -> E+E");
            reduced = 1;
        }
        // Check E -> E * E
        else if (stack_ptr >= 3 && stack[stack_ptr - 3] == 'E' && stack[stack_ptr - 2] == '*' && stack[stack_ptr - 1] == 'E') {
            stack[stack_ptr - 3] = 'E';
            stack[stack_ptr - 2] = '\0';
            stack_ptr -= 2;
            print_step("REDUCE E -> E*E");
            reduced = 1;
        }
        // Check E -> ( E )
        else if (stack_ptr >= 3 && stack[stack_ptr - 3] == '(' && stack[stack_ptr - 2] == 'E' && stack[stack_ptr - 1] == ')') {
            stack[stack_ptr - 3] = 'E';
            stack[stack_ptr - 2] = '\0';
            stack_ptr -= 2;
            print_step("REDUCE E -> (E)");
            reduced = 1;
        }
    }
}

int main() {
    printf("Enter input string (e.g. id+id*id): ");
    if (scanf("%99s", input) != 1) return 1;

    input_len = strlen(input);
    stack[0] = '\0';

    printf("\n%-20s %-20s %-20s\n", "STACK", "INPUT", "ACTION");
    printf("------------------------------------------------------------\n");
    print_step("INITIAL");

    while (i < input_len) {
        if (input[i] == 'i' && input[i+1] == 'd') {
            stack[stack_ptr++] = 'i';
            stack[stack_ptr++] = 'd';
            stack[stack_ptr] = '\0';
            i += 2;
            print_step("SHIFT id");
        } else {
            stack[stack_ptr++] = input[i++];
            stack[stack_ptr] = '\0';
            print_step("SHIFT");
        }
        check_reduce();
    }

    if (strcmp(stack, "E") == 0) {
        printf("------------------------------------------------------------\n");
        printf("RESULT: Input string is ACCEPTED (Satisfies Grammar)\n");
    } else {
        printf("------------------------------------------------------------\n");
        printf("RESULT: Input string is REJECTED (Does not satisfy Grammar)\n");
    }

    return 0;
}
