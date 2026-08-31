#include <stdio.h>
#include <string.h>

int main() {
    char str[500];

    printf("Enter a line:\n");
    fgets(str, sizeof(str), stdin);

    // Check for single-line comment
    if (strncmp(str, "//", 2) == 0) {
        printf("It is a single-line comment.\n");
    }
    // Check for multi-line comment
    else if (strncmp(str, "/*", 2) == 0) {
        if (strstr(str, "*/") != NULL)
            printf("It is a multi-line comment.\n");
        else
            printf("Incomplete multi-line comment.\n");
    }
    else {
        printf("It is not a comment.\n");
    }

    return 0;
}