"""
Admin Settings API
BULLETPROOF API for admin settings management
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Path
from typing import Dict, Any, List, Optional
from core.auth import get_current_user, get_current_admin
from core.database import get_database
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/payment-methods")
async def get_payment_methods_settings():
    """Get payment methods configuration - PUBLIC endpoint for frontend"""
    try:
        db = get_database()
        if not db:
            raise HTTPException(status_code=500, detail="Database unavailable")
        
        # Get payment methods settings (sync operation)
        setting = db['admin_settings'].find_one({'setting_key': 'payment_methods'})
        
        if setting:
            return {
                "success": True,
                "data": {
                    "paypal_enabled": setting.get('paypal_enabled', False),
                    "credit_card_enabled": setting.get('credit_card_enabled', True),
                    "stripe_enabled": setting.get('stripe_enabled', True)
                }
            }
        else:
            # Return default settings if not configured
            return {
                "success": True,
                "data": {
                    "paypal_enabled": False,
                    "credit_card_enabled": True,
                    "stripe_enabled": True
                }
            }
            
    except Exception as e:
        logger.error(f"Get payment methods settings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/payment-methods")
async def update_payment_methods_settings(
    settings: Dict[str, Any] = Body(..., description="Payment methods settings"),
    current_user: dict = Depends(get_current_admin)
):
    """Update payment methods configuration - ADMIN only"""
    try:
        db = get_database()
        if not db:
            raise HTTPException(status_code=500, detail="Database unavailable")
        
        # Update payment methods settings (sync operation)
        from datetime import datetime
        
        admin_settings = {
            'setting_key': 'payment_methods',
            'paypal_enabled': settings.get('paypal_enabled', False),
            'credit_card_enabled': settings.get('credit_card_enabled', True),
            'stripe_enabled': settings.get('stripe_enabled', True),
            'updated_at': datetime.utcnow().isoformat(),
            'updated_by': current_user.get('email', 'admin')
        }
        
        result = db['admin_settings'].update_one(
            {'setting_key': 'payment_methods'}, 
            {'$set': admin_settings}, 
            upsert=True
        )
        
        return {
            "success": True,
            "message": "Payment methods settings updated successfully",
            "data": {
                "paypal_enabled": admin_settings['paypal_enabled'],
                "credit_card_enabled": admin_settings['credit_card_enabled'],
                "stripe_enabled": admin_settings['stripe_enabled']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update payment methods settings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))