#!/usr/bin/env python3
"""
Setup script to configure admin settings in database
"""

from core.database import get_database
from datetime import datetime
import asyncio

async def setup_payment_settings():
    """Disable PayPal and configure payment methods"""
    try:
        db = get_database()
        if not db:
            print("❌ Database not available")
            return
        
        # Create admin_settings collection and disable PayPal
        admin_settings = {
            'setting_key': 'payment_methods',
            'paypal_enabled': False,
            'credit_card_enabled': True,
            'stripe_enabled': True,
            'updated_at': datetime.utcnow().isoformat(),
            'updated_by': 'admin_setup_script'
        }
        
        result = await db['admin_settings'].update_one(
            {'setting_key': 'payment_methods'}, 
            {'$set': admin_settings}, 
            upsert=True
        )
        
        print('✅ Admin payment settings configured:')
        print(f'  - PayPal: DISABLED')
        print(f'  - Credit Card: ENABLED') 
        print(f'  - Stripe: ENABLED')
        print(f'  - Modified count: {result.modified_count}')
        if result.upserted_id:
            print(f'  - Created new setting with ID: {result.upserted_id}')
        
        # Verify the setting was saved
        setting = await db['admin_settings'].find_one({'setting_key': 'payment_methods'})
        if setting:
            print('✅ Verification successful - setting saved to database')
        else:
            print('❌ Verification failed - setting not found')
            
    except Exception as e:
        print(f"❌ Error setting up admin settings: {e}")

if __name__ == "__main__":
    # Run the setup
    print("🔧 Setting up admin payment method settings...")
    asyncio.run(setup_payment_settings())
    print("✅ Admin settings setup complete")