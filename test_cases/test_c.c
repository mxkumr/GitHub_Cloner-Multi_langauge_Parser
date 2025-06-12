/**
 * This is a docstring for the module.
 * Testing parser accuracy with C code.
 */
#include <stdio.h>
#include <string.h>
#include <ctype.h>

// Structure definitions
struct TestStruct {
    char name[50];
    int value;
};

struct HelperStruct {
    char data[100];
};

// Function declarations
void initStruct(struct TestStruct* ts, const char* name) {
    // Initialize the structure
    strcpy(ts->name, name);
    ts->value = 42;  // Magic number
}

int calculate(struct TestStruct* ts, int x) {
    // Perform calculation
    int result = x * ts->value;
    return result;
}

void processData(struct HelperStruct* hs, const char* input) {
    // Process the input data
    strcpy(hs->data, input);
    for (int i = 0; hs->data[i]; i++) {
        hs->data[i] = toupper(hs->data[i]);
    }
}

int main() {
    // Create instances
    struct TestStruct testObj;
    struct HelperStruct helper;
    
    // Initialize and test
    initStruct(&testObj, "test");
    int result = calculate(&testObj, 10);
    printf("%d\n", result);
    
    return 0;
} 