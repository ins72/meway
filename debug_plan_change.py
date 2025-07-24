#!/usr/bin/env python3
"""
DEBUG PLAN CHANGE IMPACT ANALYSIS
=================================
Direct service testing to isolate the 500 error
"""

import asyncio
import sys
import os
sys.path.append('/app/backend')

from services.plan_change_impact_service import get_plan_change_impact_service

async def debug_simulate_change():
    """Debug the simulate_plan_change method directly"""
    print("🔍 DEBUGGING SIMULATE CHANGE METHOD")
    print("=" * 50)
    
    try:
        # Get service instance
        service = get_plan_change_impact_service()
        print("✅ Service instance created")
        
        # Test data from review request
        test_data = {
            "plan_name": "creator",
            "changes": {
                "pricing": {"monthly_price": 29.99}
            },
            "simulated_by": "test-user-123"
        }
        
        print(f"📝 Test data: {test_data}")
        
        # Call the method directly
        result = await service.simulate_plan_change(test_data)
        
        print(f"📊 Result success: {result.get('success')}")
        if result.get('success'):
            print(f"✅ SUCCESS: {result.get('message')}")
            simulation = result.get('simulation', {})
            print(f"   Simulation ID: {simulation.get('simulation_id')}")
            print(f"   Overall risk: {simulation.get('overall_risk')}")
            print(f"   Requires migration: {simulation.get('requires_migration')}")
            print(f"   Impact analyses: {list(simulation.get('impact_analyses', {}).keys())}")
        else:
            print(f"❌ FAILED: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()

async def debug_rollback_change():
    """Debug the rollback_plan_change method directly"""
    print("\n🔍 DEBUGGING ROLLBACK CHANGE METHOD")
    print("=" * 50)
    
    try:
        # Get service instance
        service = get_plan_change_impact_service()
        print("✅ Service instance created")
        
        # Test data from review request
        test_data = {
            "plan_name": "creator",
            "rollback_to_version": 1,
            "reason": "Test rollback",
            "rolled_back_by": "test-user-123"
        }
        
        print(f"📝 Test data: {test_data}")
        
        # Call the method directly
        result = await service.rollback_plan_change(test_data)
        
        print(f"📊 Result success: {result.get('success')}")
        if result.get('success'):
            print(f"✅ SUCCESS: {result.get('message')}")
            rollback_record = result.get('rollback_record', {})
            print(f"   Rollback ID: {rollback_record.get('_id')}")
            print(f"   Status: {rollback_record.get('status')}")
            print(f"   Rollback to version: {rollback_record.get('rollback_to_version')}")
        else:
            print(f"❌ FAILED: {result.get('error')}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Main debug function"""
    await debug_simulate_change()
    await debug_rollback_change()

if __name__ == "__main__":
    asyncio.run(main())