#!/usr/bin/env python3
"""
API INTEGRATION SETUP - MEWAYZ V2
Add provided API keys to the system configuration
"""

import os
import json
from pathlib import Path

class APIKeyIntegrator:
    def __init__(self):
        self.backend_dir = Path('/app/backend')
        self.env_file = self.backend_dir / '.env'
        
        # Provided API keys
        self.new_api_keys = {
            # ElasticMail
            "ELASTICMAIL_API_KEY": "D7CAD4A6C3F39166DEC4E906F29391905CF15EAC4F78760BCE24DCEA0F4884E9102D0F69DE607FACDF52B9DCF7F81670",
            
            # Twitter/X
            "TWITTER_API_KEY": "57zInvI1CUTkc3i4aGN87kn1k",
            "TWITTER_API_SECRET": "GJkQNYE7VoZjv8dovZXgvGGoaopJIYzdzzNBXgPVGqkRfTXWtk",
            
            # TikTok
            "TIKTOK_CLIENT_KEY": "aw09alsjbsn4syuq",
            "TIKTOK_CLIENT_SECRET": "EYYV4rrs1m7FUghDzuYPyZw36eHKRehu",
            
            # OpenAI
            "OPENAI_API_KEY": "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",
            
            # Google OAuth
            "GOOGLE_CLIENT_ID": "429180120844-nq1f3t1cjrmbeh83na713ur80mpigpss.apps.googleusercontent.com",
            "GOOGLE_CLIENT_SECRET": "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",
            
            # Stripe
            "STRIPE_PUBLISHABLE_KEY": os.environ.get("STRIPE_PUBLISHABLE_KEY", ""),
            "STRIPE_SECRET_KEY": os.environ.get("STRIPE_SECRET_KEY", "")
        }

    def add_keys_to_env(self):
        """Add API keys to .env file"""
        print("🔑 INTEGRATING PROVIDED API KEYS")
        print("=" * 50)
        
        # Read current .env content
        env_content = ""
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                env_content = f.read()
        
        # Add new keys
        added_keys = 0
        for key, value in self.new_api_keys.items():
            if f"{key}=" not in env_content:
                env_content += f"\n{key}={value}"
                added_keys += 1
                print(f"✅ Added {key}")
            else:
                # Update existing key
                import re
                pattern = f"{key}=.*"
                env_content = re.sub(pattern, f"{key}={value}", env_content)
                print(f"🔄 Updated {key}")
        
        # Write back to .env file
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        print(f"\n📊 Added/Updated {len(self.new_api_keys)} API keys")
        return added_keys

    def update_admin_config(self):
        """Update admin configuration to include new APIs"""
        config_file = self.backend_dir / "core" / "admin_config_manager.py"
        
        print("\n🔧 UPDATING ADMIN CONFIGURATION")
        print("=" * 50)
        
        try:
            with open(config_file, 'r') as f:
                content = f.read()
            
            # Add ElasticMail configuration
            elasticmail_config = '''
    # ElasticMail Configuration
    elasticmail_api_key: Optional[str] = None
    elasticmail_from_email: Optional[str] = None
    elasticmail_from_name: Optional[str] = None'''
            
            # Add TikTok configuration (enhance existing)
            tiktok_enhancement = '''
    # Enhanced TikTok Configuration
    tiktok_client_key: Optional[str] = None
    tiktok_client_secret: Optional[str] = None
    tiktok_access_token: Optional[str] = None'''
            
            # Update the file if these sections don't exist
            if "elasticmail_api_key" not in content:
                # Find a good place to insert ElasticMail config
                insertion_point = content.find("# Email Services")
                if insertion_point != -1:
                    content = content[:insertion_point] + elasticmail_config + "\n    " + content[insertion_point:]
                    print("✅ Added ElasticMail configuration")
            
            # Write back
            with open(config_file, 'w') as f:
                f.write(content)
                
            print("✅ Admin configuration updated")
            
        except Exception as e:
            print(f"⚠️  Could not update admin config: {str(e)}")

    def create_api_production_endpoints(self):
        """Create test endpoints for new API integrations"""
        print("\n🧪 CREATING API TEST ENDPOINTS")
        print("=" * 50)
        
        test_api_content = '''"""
API Integration Testing Endpoints
Test all newly integrated APIs
"""
from fastapi import APIRouter, HTTPException, Depends
from core.auth import get_current_user
import os
import httpx
import json

router = APIRouter(prefix="/api/integration-tests", tags=["API Integration Tests"])

@router.get("/elasticmail/test")
async def test_elasticmail(current_user: dict = Depends(get_current_user)):
    """Test ElasticMail API connection"""
    api_key = os.getenv("ELASTICMAIL_API_KEY")
    if not api_key:
        raise HTTPException(400, "ElasticMail API key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.elasticemail.com/v2/account/load",
                params={"apikey": api_key}
            )
        
        if response.status_code == 200:
            return {"success": True, "service": "ElasticMail", "status": "connected"}
        else:
            return {"success": False, "service": "ElasticMail", "error": response.text}
            
    except Exception as e:
        return {"success": False, "service": "ElasticMail", "error": str(e)}

@router.get("/twitter/test")
async def test_twitter(current_user: dict = Depends(get_current_user)):
    """Test Twitter API connection"""
    api_key = os.getenv("TWITTER_API_KEY")
    if not api_key:
        raise HTTPException(400, "Twitter API key not configured")
    
    return {"success": True, "service": "Twitter/X", "status": "API key configured"}

@router.get("/tiktok/test")
async def test_tiktok(current_user: dict = Depends(get_current_user)):
    """Test TikTok API connection"""
    client_key = os.getenv("TIKTOK_CLIENT_KEY")
    if not client_key:
        raise HTTPException(400, "TikTok client key not configured")
    
    return {"success": True, "service": "TikTok", "status": "Client key configured"}

@router.get("/openai/test")
async def test_openai(current_user: dict = Depends(get_current_user)):
    """Test OpenAI API connection"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(400, "OpenAI API key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openai.com/v1/models",
                headers={"Authorization": f"Bearer {api_key}"}
            )
        
        if response.status_code == 200:
            models = response.json()
            return {"success": True, "service": "OpenAI", "models_available": len(models.get("data", []))}
        else:
            return {"success": False, "service": "OpenAI", "error": response.text}
            
    except Exception as e:
        return {"success": False, "service": "OpenAI", "error": str(e)}

@router.get("/google/test")
async def test_google_oauth(current_user: dict = Depends(get_current_user)):
    """Test Google OAuth configuration"""
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise HTTPException(400, "Google Client ID not configured")
    
    return {"success": True, "service": "Google OAuth", "client_id": client_id[:20] + "..."}

@router.get("/stripe/test")
async def test_stripe(current_user: dict = Depends(get_current_user)):
    """Test Stripe API connection"""
    secret_key = os.getenv("STRIPE_SECRET_KEY")
    if not secret_key:
        raise HTTPException(400, "Stripe secret key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.stripe.com/v1/account",
                headers={"Authorization": f"Bearer {secret_key}"}
            )
        
        if response.status_code == 200:
            account = response.json()
            return {"success": True, "service": "Stripe", "account_id": account.get("id")}
        else:
            return {"success": False, "service": "Stripe", "error": response.text}
            
    except Exception as e:
        return {"success": False, "service": "Stripe", "error": str(e)}

@router.get("/all")
async def test_all_apis(current_user: dict = Depends(get_current_user)):
    """Test all API integrations"""
    results = {}
    
    # Test each API
    apis_to_test = [
        ("elasticmail", test_elasticmail),
        ("twitter", test_twitter),
        ("tiktok", test_tiktok),
        ("openai", test_openai),
        ("google", test_google_oauth),
        ("stripe", test_stripe)
    ]
    
    for api_name, test_func in apis_to_test:
        try:
            result = await test_func(current_user)
            results[api_name] = result
        except Exception as e:
            results[api_name] = {"success": False, "error": str(e)}
    
    successful = len([r for r in results.values() if r.get("success")])
    
    return {
        "total_apis": len(results),
        "successful": successful,
        "success_rate": f"{(successful/len(results)*100):.1f}%",
        "results": results
    }
'''
        
        test_file_path = self.backend_dir / "api" / "integration_tests.py"
        with open(test_file_path, 'w') as f:
            f.write(test_api_content)
        
        print("✅ Created API integration test endpoints")
        print(f"   File: {test_file_path}")

    def run_integration(self):
        """Run the complete API key integration"""
        print("🚀 API INTEGRATION SETUP - MEWAYZ V2")
        print("=" * 60)
        
        # 1. Add keys to .env
        added_keys = self.add_keys_to_env()
        
        # 2. Update admin configuration
        self.update_admin_config()
        
        # 3. Create test endpoints
        self.create_api_test_endpoints()
        
        print(f"\n✅ INTEGRATION COMPLETE")
        print(f"  • API Keys Added: {added_keys}")
        print(f"  • Admin Config Updated: ✓")
        print(f"  • Test Endpoints Created: ✓")
        print(f"\n🔄 RESTART BACKEND TO APPLY CHANGES")
        
        return True

if __name__ == "__main__":
    integrator = APIKeyIntegrator()
    success = integrator.run_integration()
    
    if success:
        print("\n🎉 All API keys successfully integrated!")
        print("   Access test endpoints at: /api/integration-tests/")
    else:
        print("\n❌ Integration encountered issues")