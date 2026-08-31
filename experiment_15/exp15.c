#include <stdio.h>
#include <ctype.h>

int main(int argc, char **argv) {
    char filename[100];
    FILE *fp;

    if (argc > 1) {
        fp = fopen(argv[1], "r");
    } else {
        printf("Enter filename: ");
        if (scanf("%99s", filename) != 1) return 1;
        fp = fopen(filename, "r");
    }

    if (!fp) {
        perror("Error opening file");
        return 1;
    }

    int chars = 0, words = 0, lines = 0;
    int in_word = 0;
    char ch;

    while ((ch = fgetc(fp)) != EOF) {
        chars++;
        if (ch == '\n') {
            lines++;
        }
        if (isspace((unsigned char)ch)) {
            in_word = 0;
        } else if (!in_word) {
            in_word = 1;
            words++;
        }
    }

    fclose(fp);

    printf("\nFile Scan Results:\n");
    printf("------------------\n");
    printf("Total Characters : %d\n", chars);
    printf("Total Words      : %d\n", words);
    printf("Total Lines      : %d\n", lines);

    return 0;
}
