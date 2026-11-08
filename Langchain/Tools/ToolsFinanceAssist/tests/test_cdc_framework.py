"""
Generic CDC Framework Test Suite
Tests all table adapters with the same test cases
"""

import sys
import time
import os

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, PROJECT_ROOT)

from Langchain.Tools.ToolsFinanceAssist.config.table_adapters import TABLE_ADAPTERS, get_adapter
from Langchain.Tools.ToolsFinanceAssist.Services.cdc_service import get_cdc_service, CDCResult


def print_section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_adapter(table_name: str):
    """Run full test suite for a single table adapter"""
    print_section(f"TESTING: {table_name.upper()}")
    
    service = get_cdc_service(table_name)
    adapter = get_adapter(table_name)
    
    # Generate unique test name
    test_name = f"TEST_{table_name}_{int(time.time())}"
    
    # Test 1: Add record
    print(f"\n[TEST 1] Add Record")
    add_data = {adapter.name_col: test_name}
    for col in adapter.value_cols:
        add_data[col] = 10000.0 if "value" in col.lower() or "amount" in col.lower() else 100.0
    for col in adapter.extra_cols:
        add_data[col] = "Test Platform"
    if adapter.date_col:
        add_data[adapter.date_col] = "2024-01-15"
    
    result = service.add_record(**add_data)
    print(f"  Result: {result.message if result.success else result.error}")
    assert result.success, f"Add failed: {result.error}"
    test_pk = result.data["pk"]
    print(f"  [OK] Added with PK: {test_pk}")
    
    # Test 2: Get current records (should include new record)
    print(f"\n[TEST 2] Get Current Records")
    current = service.get_current_records()
    test_in_current = [r for r in current if r.name == test_name]
    assert len(test_in_current) == 1, "New record should appear in current"
    assert test_in_current[0].pk == test_pk
    print(f"  [OK] Found in current records (PK: {test_in_current[0].pk})")
    
    # Test 3: Get latest record
    print(f"\n[TEST 3] Get Latest Record")
    latest = service.get_latest_record(test_name)
    assert latest is not None, "Should find latest record"
    assert latest.pk == test_pk
    assert latest.is_latest == True
    assert latest.status == "ACTIVE"
    print(f"  [OK] Latest record: PK={latest.pk}, Status={latest.status}")
    
    # Test 4: Update record (creates new version)
    print(f"\n[TEST 4] Update Record (Append-Only)")
    update_values = {}
    for col in adapter.value_cols:
        update_values[col] = 20000.0 if "value" in col.lower() or "amount" in col.lower() else 200.0
    
    result = service.update_record(test_name, **update_values)
    print(f"  Result: {result.message if result.success else result.error}")
    assert result.success, f"Update failed: {result.error}"
    old_pk = result.data["old_pk"]
    new_pk = result.data["new_pk"]
    print(f"  [OK] Old PK: {old_pk} -> New PK: {new_pk}")
    
    # Test 5: Verify chain integrity
    print(f"\n[TEST 5] Verify Chain Integrity")
    history = service.get_record_history(test_name)
    assert len(history) == 2, f"Should have 2 records, got {len(history)}"
    
    # Old record should be superseded
    old_record = [r for r in history if r.pk == old_pk][0]
    new_record = [r for r in history if r.pk == new_pk][0]
    
    assert old_record.is_latest == False, "Old record should not be latest"
    assert old_record.superseded_by == new_pk, "Old record should point to new"
    assert new_record.is_latest == True, "New record should be latest"
    assert new_record.superseded_by is None, "New record should not be superseded"
    print(f"  [OK] Chain verified: PK {old_pk} -> PK {new_pk}")
    
    # Test 6: Current view should only show latest
    print(f"\n[TEST 6] Current View Shows Only Latest")
    current = service.get_current_records()
    test_in_current = [r for r in current if r.name == test_name]
    assert len(test_in_current) == 1, "Should have exactly 1 current record"
    assert test_in_current[0].pk == new_pk, "Current should show new PK"
    print(f"  [OK] Current view shows PK: {test_in_current[0].pk}")
    
    # Test 7: Close record
    print(f"\n[TEST 7] Close Record")
    result = service.close_record(test_name)
    print(f"  Result: {result.message if result.success else result.error}")
    assert result.success, f"Close failed: {result.error}"
    closed_pk = result.data["closed_pk"]
    assert closed_pk == new_pk, "Should close the latest record"
    print(f"  [OK] Closed PK: {closed_pk}")
    
    # Test 8: Verify closed state
    print(f"\n[TEST 8] Verify Closed State")
    latest = service.get_latest_record(test_name)
    assert latest.status == "CLOSED", "Status should be CLOSED"
    assert latest.is_latest == True, "Closed record should still be latest (final state)"
    print(f"  [OK] Status: {latest.status}, Latest: {latest.is_latest}")
    
    # Test 9: Closed records view
    print(f"\n[TEST 9] Closed Records View")
    closed = service.get_closed_records()
    test_in_closed = [r for r in closed if r.name == test_name]
    assert len(test_in_closed) == 1, "Should appear in closed records"
    assert test_in_closed[0].pk == new_pk
    print(f"  [OK] Found in closed records: PK {test_in_closed[0].pk}")
    
    # Test 10: History shows full chain
    print(f"\n[TEST 10] Full History")
    history = service.get_record_history(test_name)
    assert len(history) == 2, "History should have 2 records"
    statuses = [r.status for r in history]
    assert "ACTIVE" in statuses and "CLOSED" in statuses
    print(f"  [OK] History: {[f'PK{r.pk}({r.status})' for r in history]}")
    
    # Test 11: Edge cases
    print(f"\n[TEST 11] Edge Cases")
    
    # Close already closed
    result = service.close_record(test_name)
    assert not result.success, "Should fail to close already closed"
    print(f"  [OK] Rejects close on closed record")
    
    # Update closed record
    result = service.update_record(test_name, **{adapter.value_cols[0]: 30000.0})
    assert not result.success, "Should fail to update closed record"
    print(f"  [OK] Rejects update on closed record")
    
    # Update non-existent
    result = service.update_record("NON_EXISTENT", **{adapter.value_cols[0]: 1000.0})
    assert not result.success, "Should fail for non-existent"
    print(f"  [OK] Rejects update on non-existent")
    
    # History for non-existent
    history = service.get_record_history("NON_EXISTENT")
    assert len(history) == 0, "Should return empty for non-existent"
    print(f"  [OK] Returns empty history for non-existent")
    
    print(f"\n[ALL TESTS PASSED FOR {table_name.upper()}]")
    return True


def run_all_tests():
    """Run test suite for all configured tables"""
    print("CDC FRAMEWORK - GENERIC TEST SUITE")
    print("=" * 70)
    print(f"Tables to test: {list(TABLE_ADAPTERS.keys())}")
    
    results = {}
    for table_name in TABLE_ADAPTERS.keys():
        try:
            test_adapter(table_name)
            results[table_name] = "PASS"
        except Exception as e:
            print(f"\n[FAIL] {table_name}: {e}")
            results[table_name] = f"FAIL: {e}"
    
    # Summary
    print_section("TEST SUMMARY")
    all_pass = True
    for table, result in results.items():
        status = "[PASS]" if result == "PASS" else "[FAIL]"
        print(f"  {status} {table}: {result}")
        if result != "PASS":
            all_pass = False
    
    if all_pass:
        print_section("ALL TABLES PASSED [OK]")
    else:
        print_section("SOME TESTS FAILED [FAIL]")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()