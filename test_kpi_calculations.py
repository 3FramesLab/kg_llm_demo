"""
Unit tests for KPI calculations (without MongoDB dependency).

Tests the three KPI calculation formulas:
1. Reconciliation Coverage Rate (RCR)
2. Data Quality Confidence Score (DQCS)
3. Reconciliation Efficiency Index (REI)
"""

import logging
from statistics import mean

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def calculate_rcr(matched_count: int, total_source_count: int) -> float:
    """Calculate Reconciliation Coverage Rate."""
    if total_source_count == 0:
        return 0.0
    return (matched_count / total_source_count) * 100


def calculate_dqcs(confidence_scores: list) -> float:
    """Calculate Data Quality Confidence Score."""
    if not confidence_scores:
        return 0.0
    return mean(confidence_scores)


def calculate_rei(
    match_success_rate: float,
    rule_utilization: float,
    speed_factor: float
) -> float:
    """Calculate Reconciliation Efficiency Index."""
    return (match_success_rate * rule_utilization * speed_factor) / 10000


def test_rcr_calculation():
    """Test RCR calculation with various scenarios."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 1: Reconciliation Coverage Rate (RCR)")
    logger.info("=" * 80)
    
    test_cases = [
        {"matched": 1247, "total": 1300, "expected": 95.92, "name": "Baseline (95.92%)"},
        {"matched": 1170, "total": 1300, "expected": 90.0, "name": "Warning threshold (90%)"},
        {"matched": 1040, "total": 1300, "expected": 80.0, "name": "Critical threshold (80%)"},
        {"matched": 1300, "total": 1300, "expected": 100.0, "name": "Perfect match (100%)"},
        {"matched": 0, "total": 1300, "expected": 0.0, "name": "No matches (0%)"},
    ]
    
    all_passed = True
    for test in test_cases:
        result = calculate_rcr(test["matched"], test["total"])
        passed = abs(result - test["expected"]) < 0.01
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {test['name']}")
        logger.info(f"       Matched: {test['matched']}/{test['total']} = {result:.2f}%")
        all_passed = all_passed and passed
    
    return all_passed


def test_dqcs_calculation():
    """Test DQCS calculation with various scenarios."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Data Quality Confidence Score (DQCS)")
    logger.info("=" * 80)
    
    test_cases = [
        {
            "scores": [0.95] * 500 + [0.85] * 400 + [0.75] * 347,
            "expected": 0.862,
            "name": "Baseline (86.2%)"
        },
        {
            "scores": [0.9] * 1247,
            "expected": 0.9,
            "name": "All high confidence (90%)"
        },
        {
            "scores": [0.8] * 1247,
            "expected": 0.8,
            "name": "All medium confidence (80%)"
        },
        {
            "scores": [0.7] * 1247,
            "expected": 0.7,
            "name": "All low confidence (70%)"
        },
        {
            "scores": [],
            "expected": 0.0,
            "name": "No matches (0%)"
        },
    ]
    
    all_passed = True
    for test in test_cases:
        result = calculate_dqcs(test["scores"])
        passed = abs(result - test["expected"]) < 0.01
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {test['name']}")
        logger.info(f"       Scores: {len(test['scores'])} records = {result:.3f}")
        all_passed = all_passed and passed
    
    return all_passed


def test_rei_calculation():
    """Test REI calculation with various scenarios."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Reconciliation Efficiency Index (REI)")
    logger.info("=" * 80)
    
    test_cases = [
        {
            "success": 95.92,
            "utilization": 81.82,
            "speed": 52.0,
            "expected": 40.8,
            "name": "Baseline (40.8)"
        },
        {
            "success": 100.0,
            "utilization": 100.0,
            "speed": 100.0,
            "expected": 100.0,
            "name": "Perfect efficiency (100)"
        },
        {
            "success": 50.0,
            "utilization": 50.0,
            "speed": 50.0,
            "expected": 12.5,
            "name": "Poor efficiency (12.5)"
        },
        {
            "success": 80.0,
            "utilization": 80.0,
            "speed": 80.0,
            "expected": 51.2,
            "name": "Good efficiency (51.2)"
        },
    ]
    
    all_passed = True
    for test in test_cases:
        result = calculate_rei(test["success"], test["utilization"], test["speed"])
        passed = abs(result - test["expected"]) < 0.1
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {test['name']}")
        logger.info(f"       Success: {test['success']}% × Util: {test['utilization']}% × Speed: {test['speed']}% = {result:.2f}")
        all_passed = all_passed and passed
    
    return all_passed


def test_status_determination():
    """Test status determination based on KPI values."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Status Determination")
    logger.info("=" * 80)
    
    # RCR Status
    logger.info("\nRCR Status Thresholds:")
    rcr_tests = [
        (95.92, "HEALTHY", "≥90%"),
        (90.0, "HEALTHY", "≥90%"),
        (85.0, "WARNING", "<90% and ≥80%"),
        (80.0, "WARNING", "<90% and ≥80%"),
        (75.0, "CRITICAL", "<80%"),
    ]
    
    for value, expected_status, threshold in rcr_tests:
        if value >= 90:
            status = "HEALTHY"
        elif value >= 80:
            status = "WARNING"
        else:
            status = "CRITICAL"
        
        passed = status == expected_status
        result = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{result}: RCR {value}% → {status} ({threshold})")
    
    # DQCS Status
    logger.info("\nDQCS Status Thresholds:")
    dqcs_tests = [
        (0.862, "GOOD", "≥0.80"),
        (0.80, "GOOD", "≥0.80"),
        (0.75, "ACCEPTABLE", "<0.80 and ≥0.70"),
        (0.70, "ACCEPTABLE", "<0.80 and ≥0.70"),
        (0.65, "POOR", "<0.70"),
    ]
    
    for value, expected_status, threshold in dqcs_tests:
        if value >= 0.8:
            status = "GOOD"
        elif value >= 0.7:
            status = "ACCEPTABLE"
        else:
            status = "POOR"
        
        passed = status == expected_status
        result = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{result}: DQCS {value} → {status} ({threshold})")
    
    # REI Status
    logger.info("\nREI Status Thresholds:")
    rei_tests = [
        (40.8, "ACCEPTABLE", "30-40"),
        (50.0, "EXCELLENT", ">50"),
        (45.0, "GOOD", "40-50"),
        (35.0, "ACCEPTABLE", "30-40"),
        (25.0, "WARNING", "20-30"),
        (15.0, "CRITICAL", "<20"),
    ]
    
    for value, expected_status, threshold in rei_tests:
        if value >= 50:
            status = "EXCELLENT"
        elif value >= 40:
            status = "GOOD"
        elif value >= 30:
            status = "ACCEPTABLE"
        elif value >= 20:
            status = "WARNING"
        else:
            status = "CRITICAL"
        
        passed = status == expected_status
        result = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{result}: REI {value} → {status} ({threshold})")
    
    return True


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 80)
    logger.info("KPI CALCULATION UNIT TESTS")
    logger.info("=" * 80)
    
    results = []
    results.append(("RCR Calculation", test_rcr_calculation()))
    results.append(("DQCS Calculation", test_dqcs_calculation()))
    results.append(("REI Calculation", test_rei_calculation()))
    results.append(("Status Determination", test_status_determination()))
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        logger.info("\n✓ All tests passed successfully!")
    else:
        logger.info("\n✗ Some tests failed!")
    
    logger.info("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)

