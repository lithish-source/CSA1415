%{
#include <stdio.h>
int vowel_count = 0;
int consonant_count = 0;
%}

%option noyywrap

%%

[aeiouAEIOU]                 { vowel_count++; }
[a-zA-Z]                     { consonant_count++; }
.|\n                         { /* ignore spaces, punctuation, special chars */ }

%%

int main() {
    printf("Enter a sentence: ");
    yylex();
    printf("\nNumber of Vowels: %d\n", vowel_count);
    printf("Number of Consonants: %d\n", consonant_count);
    return 0;
}
