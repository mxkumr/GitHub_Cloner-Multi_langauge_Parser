/**
 * This is a docstring for the class.
 * Testing parser accuracy with Java code.
 */
public class TestClass {
    private String name;
    private int value;
    
    // Constructor
    public TestClass(String name) {
        this.name = name;
        this.value = 42;  // Magic number
    }
    
    // Calculate method
    public int calculate(int x) {
        // Perform calculation
        int result = x * this.value;
        return result;
    }
}

class HelperClass {
    // Process data method
    public String processData(String data) {
        // Process the input
        String processed = data.toUpperCase();
        return processed;
    }
}

class Main {
    public static void main(String[] args) {
        // Create instances
        TestClass testObj = new TestClass("test");
        HelperClass helper = new HelperClass();
        
        // Test functionality
        int result = testObj.calculate(10);
        System.out.println(result);
    }
} 