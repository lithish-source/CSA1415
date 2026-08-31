%{
#include <stdio.h>
int vowel_count = 0;
int consonant_count = 0;
%}

%option noyywrap

%%

[aeiouAEIOU]    { vowel_count++; }
[a-zA-Z]        { consonant_count++; }
.|\n            { /* ignore non-alphabetic characters */ }

%%

int main() {
    printf("Enter sentence: ");
    yylex();
    printf("Number of Consonants: %d\n", consonant_count);
    printf("Number of Vowels: %d\n", vowel_count);
    return 0;
}
