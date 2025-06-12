/**
 * This is a docstring for the class.
 * Testing parser accuracy with C++ code.
 */
#include <iostream>
#include <string>

class TestClass {
private:
    std::string name;
    int value;
    
public:
    // Constructor
    TestClass(const std::string& n) : name(n), value(42) {}  // Magic number
    
    // Calculate method
    int calculate(int x) {
        // Perform calculation
        int result = x * value;
        return result;
    }
};

class HelperClass {
public:
    // Process data method
    std::string processData(const std::string& data) {
        // Process the input
        std::string processed = data;
        for (char& c : processed) {
            c = std::toupper(c);
        }
        return processed;
    }
};

int main() {
    // Create instances
    TestClass testObj("test");
    HelperClass helper;
    
    // Test functionality
    int result = testObj.calculate(10);
    std::cout << result << std::endl;
    
    return 0;
} 