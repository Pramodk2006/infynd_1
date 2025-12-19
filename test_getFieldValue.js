
// Mock the getFieldValue function from the component
const getFieldValue = (field) => {
    if (field === null || field === undefined) return null;
    if (typeof field === 'object' && field !== null && 'value' in field) {
        return field.value;
    }
    return field;
};

// Test cases
const testCases = [
    { input: "Simple String", expected: "Simple String", name: "Primitive String" },
    { input: 123, expected: 123, name: "Primitive Number" },
    { input: null, expected: null, name: "Null" },
    { input: undefined, expected: null, name: "Undefined" },
    { input: { value: "Enhanced String", confidence: 0.9, explanation: "Test" }, expected: "Enhanced String", name: "Enhanced Object" },
    { input: { value: 100, confidence: 1.0 }, expected: 100, name: "Enhanced Number" },
    { input: { other: "Object without value" }, expected: { other: "Object without value" }, name: "Regular Object" },
    { input: ["Array"], expected: ["Array"], name: "Array" }
];

let failed = false;

console.log("Running getFieldValue tests...\n");

testCases.forEach(test => {
    const result = getFieldValue(test.input);
    const passed = JSON.stringify(result) === JSON.stringify(test.expected);

    if (!passed) {
        failed = true;
        console.error(`[FAIL] ${test.name}`);
        console.error(`  Input: ${JSON.stringify(test.input)}`);
        console.error(`  Expected: ${JSON.stringify(test.expected)}`);
        console.error(`  Actual: ${JSON.stringify(result)}`);
    } else {
        console.log(`[PASS] ${test.name}`);
    }
});

if (failed) {
    console.error("\nSome tests failed!");
    process.exit(1);
} else {
    console.log("\nAll tests passed!");
}
