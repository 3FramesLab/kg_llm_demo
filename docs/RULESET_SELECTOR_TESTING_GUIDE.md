# Testing Guide: RuleSet Selector Fix

## 🧪 Test Scenarios

### Test 1: Default Option Selection
**Objective**: Verify that selecting the default "Choose a ruleset to view" option doesn't trigger errors

**Steps**:
1. Navigate to `/reconciliation` page
2. Click on "View Rules" tab
3. Click on the "Select Ruleset to View" dropdown
4. Select "Choose a ruleset to view" (the default option)

**Expected Result**:
- ✅ No error messages appear
- ✅ No console errors (check browser DevTools)
- ✅ No API calls are made
- ✅ Dropdown closes without loading anything
- ✅ No ruleset details are displayed

**Actual Result**: [To be filled during testing]

---

### Test 2: Valid RuleSet Selection
**Objective**: Verify that selecting a valid ruleset loads it correctly

**Prerequisites**:
- At least one ruleset exists in the system
- You're on the Reconciliation page, View Rules tab

**Steps**:
1. Click on the "Select Ruleset to View" dropdown
2. Select a specific ruleset (e.g., "ruleset_1 (25 rules)")
3. Wait for the page to load

**Expected Result**:
- ✅ Dropdown closes
- ✅ Selected ruleset is displayed in the dropdown
- ✅ Ruleset details appear below (name, rule count, schemas)
- ✅ Rules table is populated with the ruleset's rules
- ✅ No error messages appear
- ✅ Loading spinner appears briefly during fetch

**Actual Result**: [To be filled during testing]

---

### Test 3: Multiple RuleSet Selections
**Objective**: Verify that switching between different rulesets works smoothly

**Prerequisites**:
- At least 2 rulesets exist in the system

**Steps**:
1. Select the first ruleset from the dropdown
2. Wait for it to load
3. Select a different ruleset from the dropdown
4. Wait for it to load
5. Select the first ruleset again

**Expected Result**:
- ✅ Each selection loads the correct ruleset
- ✅ Rules table updates with the new ruleset's rules
- ✅ Ruleset details update correctly
- ✅ No errors occur during switching
- ✅ Dropdown value reflects the currently selected ruleset

**Actual Result**: [To be filled during testing]

---

### Test 4: Dropdown Rendering
**Objective**: Verify that the dropdown displays all available rulesets correctly

**Prerequisites**:
- Multiple rulesets exist in the system

**Steps**:
1. Navigate to Reconciliation page
2. Click on "View Rules" tab
3. Click on the "Select Ruleset to View" dropdown to open it

**Expected Result**:
- ✅ Dropdown opens smoothly
- ✅ Default option "Choose a ruleset to view" is visible
- ✅ All rulesets are listed with their rule counts
- ✅ Format: "ruleset_id (X rules)"
- ✅ No duplicate entries
- ✅ All rulesets are selectable

**Actual Result**: [To be filled during testing]

---

### Test 5: Empty RuleSet List
**Objective**: Verify behavior when no rulesets exist

**Prerequisites**:
- No rulesets exist in the system (or delete all rulesets)

**Steps**:
1. Navigate to Reconciliation page
2. Click on "View Rules" tab

**Expected Result**:
- ✅ Dropdown is NOT displayed (hidden by `rulesets.length > 0` check)
- ✅ Info message appears: "No rulesets available. Generate rules using the 'Generate Rules' tab."
- ✅ No errors occur

**Actual Result**: [To be filled during testing]

---

### Test 6: Browser Console Check
**Objective**: Verify no JavaScript errors occur during dropdown interactions

**Steps**:
1. Open browser DevTools (F12)
2. Go to Console tab
3. Navigate to Reconciliation page
4. Perform Tests 1-3 above
5. Check console for errors

**Expected Result**:
- ✅ No red error messages in console
- ✅ No warnings related to the dropdown
- ✅ No failed API requests (404, 500, etc.)
- ✅ Only normal info/debug messages

**Actual Result**: [To be filled during testing]

---

### Test 7: Network Tab Check
**Objective**: Verify correct API calls are made

**Steps**:
1. Open browser DevTools (F12)
2. Go to Network tab
3. Navigate to Reconciliation page
4. Select a ruleset from the dropdown
5. Check the network requests

**Expected Result**:
- ✅ When default option selected: NO new API calls
- ✅ When valid ruleset selected: ONE API call to `/api/v1/reconciliation/rulesets/{id}`
- ✅ API response status: 200 OK
- ✅ Response contains ruleset data with rules array

**Actual Result**: [To be filled during testing]

---

### Test 8: Mobile Responsiveness
**Objective**: Verify dropdown works on mobile devices

**Steps**:
1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select a mobile device (e.g., iPhone 12)
4. Navigate to Reconciliation page
5. Test dropdown selection

**Expected Result**:
- ✅ Dropdown is fully visible and usable
- ✅ Text is readable
- ✅ Selection works smoothly
- ✅ No layout issues
- ✅ Rules table is responsive

**Actual Result**: [To be filled during testing]

---

## 📋 Test Checklist

- [ ] Test 1: Default option selection - No errors
- [ ] Test 2: Valid ruleset selection - Loads correctly
- [ ] Test 3: Multiple selections - Switching works
- [ ] Test 4: Dropdown rendering - All rulesets visible
- [ ] Test 5: Empty list - Proper message shown
- [ ] Test 6: Console - No errors
- [ ] Test 7: Network - Correct API calls
- [ ] Test 8: Mobile - Responsive and functional

---

## 🐛 Bug Report Template

If you find any issues during testing, please report them with:

**Title**: [Brief description of the issue]

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Result**:
[What should happen]

**Actual Result**:
[What actually happened]

**Browser/Device**:
[Browser name and version, device type]

**Screenshots/Console Errors**:
[Attach any relevant screenshots or console errors]

---

## ✅ Sign-Off

**Tested By**: [Your name]
**Date**: [Date of testing]
**Status**: [PASS / FAIL]
**Notes**: [Any additional notes]

---

## 📞 Support

If you encounter any issues:
1. Check the browser console for errors (F12 → Console)
2. Check the Network tab for failed API calls
3. Verify rulesets exist in the system
4. Try refreshing the page
5. Clear browser cache and try again

For persistent issues, please report with the bug report template above.

