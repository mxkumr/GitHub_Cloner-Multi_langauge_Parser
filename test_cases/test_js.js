/**
 * This is a docstring for the module.
 * Testing parser accuracy with JavaScript code.
 */

// Class definitions
class TestClass {
    constructor(name) {
        this.name = name;
        this.value = 42;  // Magic number
    }

    calculate(x) {
        // Perform calculation
        return x * this.value;
    }
}

class HelperClass {
    processData(input) {
        // Process the input data
        return input.toUpperCase();
    }
}

// Function declarations
function initTest(name) {
    // Initialize test object
    return new TestClass(name);
}

function runTest() {
    // Create instances
    const testObj = initTest("test");
    const helper = new HelperClass();
    
    // Test the functionality
    const result = testObj.calculate(10);
    console.log(result);
}

// Run the test
runTest(); 