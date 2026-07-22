#include <stdio.h>

int main() {
    FILE *fp;
    char ch;
    int spaces = 0, tabs = 0, newlines = 0;

    fp = fopen("input.txt", "r");

    if (fp == NULL) {
        printf("Cannot open file.\n");
        return 0;
    }

    while ((ch = fgetc(fp)) != EOF) {
        if (ch == ' ')
            spaces++;
        else if (ch == '\t')
            tabs++;
        else if (ch == '\n')
            newlines++;
    }

    fclose(fp);

    printf("Number of Spaces      : %d\n", spaces);
    printf("Number of Tabs        : %d\n", tabs);
    printf("Number of Newlines    : %d\n", newlines);
    printf("Total Whitespaces     : %d\n", spaces + tabs);

}