#include <stdio.h>
#include <ctype.h>
#include <string.h>

char *keywords[] = {
    "int", "float", "char", "double", "if", "else",
    "while", "for", "return", "void", "break",
    "continue", "switch", "case", "default"
};

int isKeyword(char str[]) {
    int n = sizeof(keywords) / sizeof(keywords[0]);
    for (int i = 0; i < n; i++) {
        if (strcmp(str, keywords[i]) == 0)
            return 1;
    }
    return 0;
}

int main() {
    FILE *fp;
    char ch, word[100];
    int i;

    fp = fopen("input.c", "r");

    if (fp == NULL) {
        printf("File not found.\n");
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
                continue;
            }

            // Multi-line comment
            else if (next == '*') {
                while ((ch = fgetc(fp)) != EOF) {
                    if (ch == '*') {
                        next = fgetc(fp);
                        if (next == '/')
                            break;
                        else
                            ungetc(next, fp);
                    }
                }
                continue;
            }

            else {
                printf("Operator : /\n");
                ungetc(next, fp);
            }
        }

        // Identifier or Keyword
        if (isalpha(ch) || ch == '_') {
            i = 0;
            word[i++] = ch;

            while ((ch = fgetc(fp)) != EOF &&
                  (isalnum(ch) || ch == '_')) {
                word[i++] = ch;
            }

            word[i] = '\0';

            if (isKeyword(word))
                printf("Keyword    : %s\n", word);
            else
                printf("Identifier : %s\n", word);

            if (ch != EOF)
                ungetc(ch, fp);
        }

        // Constant
        else if (isdigit(ch)) {
            i = 0;
            word[i++] = ch;

            while ((ch = fgetc(fp)) != EOF && isdigit(ch))
                word[i++] = ch;

            word[i] = '\0';

            printf("Constant   : %s\n", word);

            if (ch != EOF)
                ungetc(ch, fp);
        }

        // Operators
        else if (strchr("+-*=<>!%", ch))
            printf("Operator   : %c\n", ch);

        // Special Symbols
        else if (strchr("(){}[];,", ch))
            printf("Symbol     : %c\n", ch);
    }

    fclose(fp);
    return 0;
}