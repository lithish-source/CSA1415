#include <stdio.h>
#include <ctype.h>
#include <string.h>

int main() {
    FILE *fp;
    char ch, str[50];
    int i;

    fp = fopen("input.c", "r");

    if (fp == NULL) {
        printf("Cannot open file.\n");
        return 0;
    }

    while ((ch = fgetc(fp)) != EOF) {

        // Ignore spaces, tabs and new lines
        if (isspace(ch))
            continue;

        // Ignore comments
        if (ch == '/') {
            char next = fgetc(fp);

            // Single-line comment
            if (next == '/') {
                while ((ch = fgetc(fp)) != '\n' && ch != EOF);
            }
            // Multi-line comment
            else if (next == '*') {
                while ((ch = fgetc(fp)) != EOF) {
                    if (ch == '*' && (next = fgetc(fp)) == '/')
                        break;
                    else
                        ungetc(next, fp);
                }
            }
            else {
                printf("Operator: /\n");
                ungetc(next, fp);
            }
        }

        // Identifier
        else if (isalpha(ch) || ch == '_') {
            i = 0;
            str[i++] = ch;

            while ((ch = fgetc(fp)) != EOF && (isalnum(ch) || ch == '_'))
                str[i++] = ch;

            str[i] = '\0';
            printf("Identifier: %s\n", str);

            if (ch != EOF)
                ungetc(ch, fp);
        }

        // Constant
        else if (isdigit(ch)) {
            i = 0;
            str[i++] = ch;

            while ((ch = fgetc(fp)) != EOF && isdigit(ch))
                str[i++] = ch;

            str[i] = '\0';
            printf("Constant: %s\n", str);

            if (ch != EOF)
                ungetc(ch, fp);
        }

        // Operators
        else if (ch == '+' || ch == '-' || ch == '*' ||
                 ch == '=' || ch == '<' || ch == '>' ||
                 ch == '%' || ch == '!') {
            printf("Operator: %c\n", ch);
        }
    }

    fclose(fp);
    return 0;
}