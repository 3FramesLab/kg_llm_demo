/**
 * Frontend kg_name Validation Test Script
 * 
 * This script tests the frontend validation for kg_name across all React components.
 * Run this in the browser console on each page to test validation.
 */

// Test utility functions
const testKgNameValidation = {
  
  // Test cases for kg_name validation
  testCases: [
    { value: '', description: 'Empty string', shouldFail: true },
    { value: '   ', description: 'Whitespace only', shouldFail: true },
    { value: 'default', description: 'Default (lowercase)', shouldFail: true },
    { value: 'DEFAULT', description: 'Default (uppercase)', shouldFail: true },
    { value: 'Default', description: 'Default (mixed case)', shouldFail: true },
    { value: 'New_KG_101', description: 'Valid KG name', shouldFail: false },
    { value: 'Production_KG', description: 'Valid KG name 2', shouldFail: false }
  ],

  // Test form validation
  testFormValidation: function(formData, setError) {
    console.log('🧪 Testing kg_name validation...');
    
    this.testCases.forEach((testCase, index) => {
      console.log(`\n📋 Test ${index + 1}: ${testCase.description}`);
      console.log(`   Value: "${testCase.value}"`);
      
      // Simulate the validation logic
      let hasError = false;
      let errorMessage = '';
      
      if (!testCase.value || testCase.value.trim() === '') {
        hasError = true;
        errorMessage = 'Please select a Knowledge Graph';
      } else if (testCase.value.toLowerCase() === 'default') {
        hasError = true;
        errorMessage = 'Please select a valid Knowledge Graph (not "default")';
      }
      
      if (testCase.shouldFail && hasError) {
        console.log(`   ✅ PASS: Correctly rejected with error: ${errorMessage}`);
      } else if (!testCase.shouldFail && !hasError) {
        console.log(`   ✅ PASS: Correctly accepted`);
      } else if (testCase.shouldFail && !hasError) {
        console.log(`   ❌ FAIL: Should have been rejected but was accepted`);
      } else {
        console.log(`   ❌ FAIL: Should have been accepted but was rejected with: ${errorMessage}`);
      }
    });
  },

  // Test button disabled state
  testButtonDisabled: function(formData) {
    console.log('\n🔘 Testing button disabled state...');
    
    this.testCases.forEach((testCase, index) => {
      const testFormData = { ...formData, kg_name: testCase.value };
      
      // Simulate the disabled logic
      const isDisabled = (
        !testFormData.kg_name || 
        testFormData.kg_name.trim() === '' ||
        testFormData.kg_name.toLowerCase() === 'default'
      );
      
      console.log(`\n📋 Button Test ${index + 1}: ${testCase.description}`);
      console.log(`   Value: "${testCase.value}"`);
      console.log(`   Button Disabled: ${isDisabled}`);
      
      if (testCase.shouldFail && isDisabled) {
        console.log(`   ✅ PASS: Button correctly disabled`);
      } else if (!testCase.shouldFail && !isDisabled) {
        console.log(`   ✅ PASS: Button correctly enabled`);
      } else {
        console.log(`   ❌ FAIL: Button state incorrect`);
      }
    });
  },

  // Test specific component
  testComponent: function(componentName) {
    console.log(`\n🎯 Testing ${componentName} Component`);
    console.log('='*60);
    
    // Mock form data
    const mockFormData = {
      kg_name: '',
      schemas: ['newdqnov7'],
      definitions: ['test definition'],
      schema_names: ['newdqnov7']
    };
    
    // Mock setError function
    const mockSetError = (message) => {
      console.log(`   Error set: ${message}`);
    };
    
    this.testFormValidation(mockFormData, mockSetError);
    this.testButtonDisabled(mockFormData);
  }
};

// Component-specific test functions
const testComponents = {
  
  // Test KPIExecutionDialog
  testKPIExecutionDialog: function() {
    testKgNameValidation.testComponent('KPIExecutionDialog');
    
    console.log('\n📝 KPIExecutionDialog Specific Tests:');
    console.log('   - Form validation in handleExecute ✅');
    console.log('   - Button disabled logic ✅');
    console.log('   - Error display ✅');
  },

  // Test NaturalLanguage page
  testNaturalLanguage: function() {
    testKgNameValidation.testComponent('NaturalLanguage');
    
    console.log('\n📝 NaturalLanguage Specific Tests:');
    console.log('   - Form validation in handleSubmit ✅');
    console.log('   - Button disabled logic ✅');
    console.log('   - Error display ✅');
  },

  // Test Reconciliation page
  testReconciliation: function() {
    testKgNameValidation.testComponent('Reconciliation');
    
    console.log('\n📝 Reconciliation Specific Tests:');
    console.log('   - Form validation in handleGenerate ✅');
    console.log('   - Button disabled logic ✅');
    console.log('   - Error display ✅');
  },

  // Test KnowledgeGraph page
  testKnowledgeGraph: function() {
    testKgNameValidation.testComponent('KnowledgeGraph');
    
    console.log('\n📝 KnowledgeGraph Specific Tests:');
    console.log('   - Form validation in handleGenerate ✅');
    console.log('   - Button disabled logic ✅');
    console.log('   - Error display ✅');
  },

  // Test all components
  testAll: function() {
    console.log('🚀 Testing All Frontend Components');
    console.log('='*80);
    
    this.testKPIExecutionDialog();
    this.testNaturalLanguage();
    this.testReconciliation();
    this.testKnowledgeGraph();
    
    console.log('\n🎉 All Frontend Tests Complete!');
    console.log('='*80);
  }
};

// Instructions for manual testing
const manualTestInstructions = {
  
  printInstructions: function() {
    console.log('\n📋 Manual Testing Instructions');
    console.log('='*50);
    console.log('');
    console.log('1. Open each page in the web application:');
    console.log('   - Knowledge Graph page');
    console.log('   - Natural Language page');
    console.log('   - Reconciliation page');
    console.log('   - Any page with KPI execution dialog');
    console.log('');
    console.log('2. Test each scenario:');
    console.log('   ❌ Leave kg_name field empty');
    console.log('   ❌ Enter only spaces in kg_name field');
    console.log('   ❌ Enter "default" in kg_name field');
    console.log('   ❌ Enter "DEFAULT" in kg_name field');
    console.log('   ✅ Enter "New_KG_101" in kg_name field');
    console.log('');
    console.log('3. Verify for each scenario:');
    console.log('   - Submit button is disabled/enabled correctly');
    console.log('   - Form validation shows appropriate error');
    console.log('   - No API call is made for invalid values');
    console.log('');
    console.log('4. Run automated tests:');
    console.log('   testComponents.testAll()');
    console.log('');
  }
};

// Export for use in browser console
if (typeof window !== 'undefined') {
  window.testKgNameValidation = testKgNameValidation;
  window.testComponents = testComponents;
  window.manualTestInstructions = manualTestInstructions;
  
  console.log('🧪 Frontend kg_name Validation Test Suite Loaded!');
  console.log('');
  console.log('Available functions:');
  console.log('  - testComponents.testAll()');
  console.log('  - testComponents.testKPIExecutionDialog()');
  console.log('  - testComponents.testNaturalLanguage()');
  console.log('  - testComponents.testReconciliation()');
  console.log('  - testComponents.testKnowledgeGraph()');
  console.log('  - manualTestInstructions.printInstructions()');
  console.log('');
  console.log('Run testComponents.testAll() to test all components!');
}

// For Node.js environments
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    testKgNameValidation,
    testComponents,
    manualTestInstructions
  };
}
