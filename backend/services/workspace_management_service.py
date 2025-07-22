"""
Workspace Management Service
Mewayz v2 - July 22, 2025
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.workspace_models import (
    WorkspaceCreate, WorkspaceUpdate, WorkspaceResponse,
    WorkspaceMemberInvite, WorkspaceMemberUpdate, WorkspaceMemberResponse,
    WorkspaceSubscription, WorkspaceAnalytics, WorkspaceOnboarding,
    WorkspaceRole, SubscriptionPlan, MainGoal, WorkspaceStatus
)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class WorkspaceManagementService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.workspaces = db["workspaces"]
        self.workspace_members = db["workspace_members"]
        self.workspace_subscriptions = db["workspace_subscriptions"]
        self.workspace_analytics = db["workspace_analytics"]
        self.workspace_onboarding = db["workspace_onboarding"]
        self.workspace_invitations = db["workspace_invitations"]
        self.users = db["users"]
        
        # Feature configurations
        self.FEATURE_CATALOG = {
            "instagram": {
                "name": "Instagram Lead Generation",
                "description": "Advanced Instagram lead discovery and contact extraction",
                "category": "social_media",
                "icon": "instagram",
                "color": "#E4405F"
            },
            "link_in_bio": {
                "name": "Link in Bio Builder",
                "description": "Create stunning bio link pages with drag-and-drop",
                "category": "content",
                "icon": "link",
                "color": "#00D4AA"
            },
            "courses": {
                "name": "Course & Community",
                "description": "Build and sell online courses with community features",
                "category": "education",
                "icon": "graduation-cap",
                "color": "#F59E0B"
            },
            "ecommerce": {
                "name": "E-commerce Store",
                "description": "Complete online store with payment processing",
                "category": "business",
                "icon": "shopping-cart",
                "color": "#8B5CF6"
            },
            "crm": {
                "name": "CRM & Lead Management",
                "description": "Manage leads and customer relationships",
                "category": "business",
                "icon": "users",
                "color": "#EF4444"
            },
            "analytics": {
                "name": "Advanced Analytics",
                "description": "Comprehensive business analytics and reporting",
                "category": "analytics",
                "icon": "chart-bar",
                "color": "#06B6D4"
            },
            "email_marketing": {
                "name": "Email Marketing",
                "description": "Create and manage email campaigns",
                "category": "marketing",
                "icon": "mail",
                "color": "#10B981"
            },
            "social_posting": {
                "name": "Social Media Posting",
                "description": "Schedule and manage social media content",
                "category": "social_media",
                "icon": "share",
                "color": "#3B82F6"
            },
            "website_builder": {
                "name": "Website Builder",
                "description": "Build professional websites with no-code",
                "category": "content",
                "icon": "desktop-computer",
                "color": "#6366F1"
            },
            "booking_system": {
                "name": "Booking System",
                "description": "Appointment scheduling and management",
                "category": "business",
                "icon": "calendar",
                "color": "#F97316"
            }
        }
        
        self.SUBSCRIPTION_PLANS = {
            SubscriptionPlan.FREE: {
                "name": "Free Plan",
                "description": "Get started with basic features",
                "feature_limit": 3,
                "monthly_cost": 0,
                "yearly_cost": 0,
                "features_included": ["link_in_bio", "social_posting", "crm"],
                "limitations": {
                    "branding": True,
                    "team_members": 1,
                    "storage": "1GB",
                    "api_calls": 1000
                }
            },
            SubscriptionPlan.PRO: {
                "name": "Pro Plan",
                "description": "Advanced features for growing businesses",
                "feature_limit": 999,
                "monthly_cost_per_feature": 1.0,
                "yearly_cost_per_feature": 10.0,
                "features_included": "all",
                "limitations": {
                    "branding": True,
                    "team_members": 10,
                    "storage": "100GB",
                    "api_calls": 50000
                }
            },
            SubscriptionPlan.ENTERPRISE: {
                "name": "Enterprise Plan",
                "description": "White-label solution for agencies",
                "feature_limit": 999,
                "monthly_cost_per_feature": 1.5,
                "yearly_cost_per_feature": 15.0,
                "features_included": "all",
                "limitations": {
                    "branding": False,
                    "team_members": 999,
                    "storage": "1TB",
                    "api_calls": 999999,
                    "whitelabel": True
                }
            }
        }

    async def create_workspace(self, user_id: str, workspace_data: WorkspaceCreate) -> WorkspaceResponse:
        """Create a new workspace"""
        try:
            workspace_id = str(uuid.uuid4())
            current_time = datetime.utcnow()
            
            # Calculate enabled features based on subscription plan
            enabled_features = await self._calculate_enabled_features(
                workspace_data.subscription_plan,
                workspace_data.main_goals
            )
            
            workspace_doc = {
                "_id": workspace_id,
                "name": workspace_data.name,
                "description": workspace_data.description,
                "industry": workspace_data.industry,
                "website": workspace_data.website,
                "main_goals": [goal.value for goal in workspace_data.main_goals],
                "subscription_plan": workspace_data.subscription_plan.value,
                "branding": workspace_data.branding or self._get_default_branding(),
                "settings": workspace_data.settings or self._get_default_settings(),
                "status": WorkspaceStatus.ACTIVE.value,
                "owner_id": user_id,
                "created_at": current_time,
                "updated_at": current_time,
                "features_enabled": enabled_features
            }
            
            # Insert workspace
            await self.workspaces.insert_one(workspace_doc)
            
            # Add owner as workspace member
            await self._add_workspace_member(
                workspace_id, user_id, WorkspaceRole.OWNER, user_id
            )
            
            # Create subscription record
            await self._create_workspace_subscription(workspace_id, workspace_data.subscription_plan, enabled_features)
            
            # Initialize analytics
            await self._initialize_workspace_analytics(workspace_id)
            
            # Create onboarding flow
            await self._create_onboarding_flow(workspace_id, workspace_data.main_goals)
            
            return await self._format_workspace_response(workspace_doc)
            
        except Exception as e:
            raise Exception(f"Failed to create workspace: {str(e)}")

    async def get_user_workspaces(self, user_id: str) -> List[WorkspaceResponse]:
        """Get all workspaces for a user"""
        try:
            # Get workspaces where user is a member
            member_records = await self.workspace_members.find(
                {"user_id": user_id, "status": "active"}
            ).to_list(length=None)
            
            workspace_ids = [record["workspace_id"] for record in member_records]
            
            if not workspace_ids:
                return []
            
            # Get workspace details
            workspaces = await self.workspaces.find(
                {"_id": {"$in": workspace_ids}, "status": {"$ne": "deleted"}}
            ).to_list(length=None)
            
            # Format responses
            responses = []
            for workspace in workspaces:
                response = await self._format_workspace_response(workspace)
                responses.append(response)
            
            return sorted(responses, key=lambda x: x.created_at, reverse=True)
            
        except Exception as e:
            raise Exception(f"Failed to get user workspaces: {str(e)}")

    async def get_workspace_by_id(self, workspace_id: str, user_id: str) -> WorkspaceResponse:
        """Get workspace by ID with user permission check"""
        try:
            # Check if user has access to workspace
            member_record = await self.workspace_members.find_one({
                "workspace_id": workspace_id,
                "user_id": user_id,
                "status": "active"
            })
            
            if not member_record:
                raise Exception("Access denied or workspace not found")
            
            # Get workspace
            workspace = await self.workspaces.find_one({"_id": workspace_id})
            if not workspace:
                raise Exception("Workspace not found")
            
            return await self._format_workspace_response(workspace)
            
        except Exception as e:
            raise Exception(f"Failed to get workspace: {str(e)}")

    async def update_workspace(self, workspace_id: str, user_id: str, update_data: WorkspaceUpdate) -> WorkspaceResponse:
        """Update workspace (owner/admin only)"""
        try:
            # Check permissions
            await self._check_workspace_permission(workspace_id, user_id, [WorkspaceRole.OWNER, WorkspaceRole.ADMIN])
            
            # Prepare update document
            update_doc = {"updated_at": datetime.utcnow()}
            
            if update_data.name is not None:
                update_doc["name"] = update_data.name
            if update_data.description is not None:
                update_doc["description"] = update_data.description
            if update_data.industry is not None:
                update_doc["industry"] = update_data.industry
            if update_data.website is not None:
                update_doc["website"] = update_data.website
            if update_data.main_goals is not None:
                update_doc["main_goals"] = [goal.value for goal in update_data.main_goals]
                # Recalculate enabled features
                workspace = await self.workspaces.find_one({"_id": workspace_id})
                enabled_features = await self._calculate_enabled_features(
                    SubscriptionPlan(workspace["subscription_plan"]),
                    update_data.main_goals
                )
                update_doc["features_enabled"] = enabled_features
            if update_data.branding is not None:
                update_doc["branding"] = update_data.branding
            if update_data.settings is not None:
                update_doc["settings"] = update_data.settings
            if update_data.status is not None:
                update_doc["status"] = update_data.status.value
            
            # Update workspace
            await self.workspaces.update_one(
                {"_id": workspace_id},
                {"$set": update_doc}
            )
            
            # Get updated workspace
            updated_workspace = await self.workspaces.find_one({"_id": workspace_id})
            return await self._format_workspace_response(updated_workspace)
            
        except Exception as e:
            raise Exception(f"Failed to update workspace: {str(e)}")

    async def invite_workspace_member(self, workspace_id: str, inviter_id: str, invite_data: WorkspaceMemberInvite) -> Dict[str, Any]:
        """Invite a user to workspace"""
        try:
            # Check permissions
            await self._check_workspace_permission(workspace_id, inviter_id, [WorkspaceRole.OWNER, WorkspaceRole.ADMIN])
            
            # Check if user already invited or is member
            existing_member = await self.workspace_members.find_one({
                "workspace_id": workspace_id,
                "email": invite_data.email
            })
            
            if existing_member:
                if existing_member["status"] == "active":
                    raise Exception("User is already a member of this workspace")
                elif existing_member["status"] == "invited":
                    raise Exception("User has already been invited")
            
            # Check workspace limits
            workspace = await self.workspaces.find_one({"_id": workspace_id})
            subscription = await self.workspace_subscriptions.find_one({"workspace_id": workspace_id})
            
            current_members = await self.workspace_members.count_documents({
                "workspace_id": workspace_id,
                "status": "active"
            })
            
            plan_limits = self.SUBSCRIPTION_PLANS[SubscriptionPlan(subscription["plan"])]
            if current_members >= plan_limits["limitations"]["team_members"]:
                raise Exception("Workspace member limit reached for current plan")
            
            # Create invitation
            invitation_id = str(uuid.uuid4())
            invitation_token = str(uuid.uuid4())
            
            invitation_doc = {
                "_id": invitation_id,
                "workspace_id": workspace_id,
                "email": invite_data.email,
                "first_name": invite_data.first_name,
                "last_name": invite_data.last_name,
                "role": invite_data.role.value,
                "status": "invited",
                "invitation_token": invitation_token,
                "message": invite_data.message,
                "invited_by": inviter_id,
                "invited_at": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(days=7)
            }
            
            await self.workspace_invitations.insert_one(invitation_doc)
            
            # Send invitation email
            await self._send_invitation_email(
                invite_data.email,
                workspace["name"],
                invitation_token,
                invite_data.first_name,
                invite_data.message
            )
            
            return {
                "invitation_id": invitation_id,
                "email": invite_data.email,
                "role": invite_data.role.value,
                "status": "invited",
                "expires_at": invitation_doc["expires_at"]
            }
            
        except Exception as e:
            raise Exception(f"Failed to invite member: {str(e)}")

    async def accept_workspace_invitation(self, invitation_token: str, user_id: str) -> Dict[str, Any]:
        """Accept workspace invitation"""
        try:
            # Find invitation
            invitation = await self.workspace_invitations.find_one({
                "invitation_token": invitation_token,
                "status": "invited"
            })
            
            if not invitation:
                raise Exception("Invalid or expired invitation")
            
            if invitation["expires_at"] < datetime.utcnow():
                raise Exception("Invitation has expired")
            
            # Get user email
            user = await self.users.find_one({"_id": user_id})
            if not user or user["email"] != invitation["email"]:
                raise Exception("Invitation email does not match user email")
            
            # Add user to workspace
            await self._add_workspace_member(
                invitation["workspace_id"],
                user_id,
                WorkspaceRole(invitation["role"]),
                invitation["invited_by"]
            )
            
            # Update invitation status
            await self.workspace_invitations.update_one(
                {"_id": invitation["_id"]},
                {"$set": {"status": "accepted", "accepted_at": datetime.utcnow()}}
            )
            
            # Get workspace info
            workspace = await self.workspaces.find_one({"_id": invitation["workspace_id"]})
            
            return {
                "workspace_id": invitation["workspace_id"],
                "workspace_name": workspace["name"],
                "role": invitation["role"],
                "status": "accepted"
            }
            
        except Exception as e:
            raise Exception(f"Failed to accept invitation: {str(e)}")

    async def get_workspace_members(self, workspace_id: str, user_id: str) -> List[WorkspaceMemberResponse]:
        """Get all workspace members"""
        try:
            # Check permissions
            await self._check_workspace_permission(workspace_id, user_id, [WorkspaceRole.OWNER, WorkspaceRole.ADMIN])
            
            # Get members
            members = await self.workspace_members.find(
                {"workspace_id": workspace_id}
            ).to_list(length=None)
            
            responses = []
            for member in members:
                response = WorkspaceMemberResponse(
                    id=member["_id"],
                    workspace_id=member["workspace_id"],
                    user_id=member["user_id"],
                    email=member["email"],
                    first_name=member.get("first_name"),
                    last_name=member.get("last_name"),
                    role=WorkspaceRole(member["role"]),
                    status=member["status"],
                    permissions=member.get("permissions", {}),
                    invited_at=member["invited_at"],
                    joined_at=member.get("joined_at"),
                    last_active=member.get("last_active"),
                    invited_by=member["invited_by"]
                )
                responses.append(response)
            
            return responses
            
        except Exception as e:
            raise Exception(f"Failed to get workspace members: {str(e)}")

    async def get_workspace_analytics(self, workspace_id: str, user_id: str) -> WorkspaceAnalytics:
        """Get workspace analytics"""
        try:
            # Check permissions
            await self._check_workspace_permission(workspace_id, user_id, [WorkspaceRole.OWNER, WorkspaceRole.ADMIN])
            
            # Get analytics
            analytics = await self.workspace_analytics.find_one({"workspace_id": workspace_id})
            
            if not analytics:
                # Create default analytics
                analytics = await self._initialize_workspace_analytics(workspace_id)
            
            return WorkspaceAnalytics(**analytics)
            
        except Exception as e:
            raise Exception(f"Failed to get workspace analytics: {str(e)}")

    async def get_available_features(self) -> Dict[str, Any]:
        """Get all available features catalog"""
        return {
            "features": self.FEATURE_CATALOG,
            "categories": list(set(f["category"] for f in self.FEATURE_CATALOG.values())),
            "subscription_plans": self.SUBSCRIPTION_PLANS
        }

    # Helper methods
    async def _calculate_enabled_features(self, plan: SubscriptionPlan, main_goals: List[MainGoal]) -> List[str]:
        """Calculate enabled features based on subscription plan and main goals"""
        if plan == SubscriptionPlan.FREE:
            # Free plan gets 3 basic features
            return [goal.value for goal in main_goals[:3]]
        else:
            # Pro and Enterprise get all features
            return list(self.FEATURE_CATALOG.keys())

    async def _format_workspace_response(self, workspace_doc: Dict[str, Any]) -> WorkspaceResponse:
        """Format workspace document to response model"""
        # Get team count
        team_count = await self.workspace_members.count_documents({
            "workspace_id": workspace_doc["_id"],
            "status": "active"
        })
        
        return WorkspaceResponse(
            id=workspace_doc["_id"],
            name=workspace_doc["name"],
            description=workspace_doc.get("description"),
            industry=workspace_doc.get("industry"),
            website=workspace_doc.get("website"),
            main_goals=[MainGoal(goal) for goal in workspace_doc.get("main_goals", [])],
            subscription_plan=SubscriptionPlan(workspace_doc["subscription_plan"]),
            branding=workspace_doc.get("branding", {}),
            settings=workspace_doc.get("settings", {}),
            status=WorkspaceStatus(workspace_doc["status"]),
            owner_id=workspace_doc["owner_id"],
            created_at=workspace_doc["created_at"],
            updated_at=workspace_doc["updated_at"],
            team_count=team_count,
            features_enabled=workspace_doc.get("features_enabled", [])
        )

    async def _add_workspace_member(self, workspace_id: str, user_id: str, role: WorkspaceRole, invited_by: str):
        """Add user as workspace member"""
        member_id = str(uuid.uuid4())
        user = await self.users.find_one({"_id": user_id})
        
        member_doc = {
            "_id": member_id,
            "workspace_id": workspace_id,
            "user_id": user_id,
            "email": user["email"],
            "first_name": user.get("first_name"),
            "last_name": user.get("last_name"),
            "role": role.value,
            "status": "active",
            "permissions": self._get_role_permissions(role),
            "invited_by": invited_by,
            "invited_at": datetime.utcnow(),
            "joined_at": datetime.utcnow(),
            "last_active": datetime.utcnow()
        }
        
        await self.workspace_members.insert_one(member_doc)

    async def _check_workspace_permission(self, workspace_id: str, user_id: str, required_roles: List[WorkspaceRole]):
        """Check if user has required permissions for workspace"""
        member = await self.workspace_members.find_one({
            "workspace_id": workspace_id,
            "user_id": user_id,
            "status": "active"
        })
        
        if not member:
            raise Exception("Access denied")
        
        if WorkspaceRole(member["role"]) not in required_roles:
            raise Exception("Insufficient permissions")

    async def _create_workspace_subscription(self, workspace_id: str, plan: SubscriptionPlan, features: List[str]):
        """Create workspace subscription record"""
        plan_config = self.SUBSCRIPTION_PLANS[plan]
        
        subscription_doc = {
            "_id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "plan": plan.value,
            "features_enabled": features,
            "feature_count": len(features),
            "monthly_cost": self._calculate_monthly_cost(plan, len(features)),
            "yearly_cost": self._calculate_yearly_cost(plan, len(features)),
            "billing_cycle": "monthly",
            "next_billing_date": datetime.utcnow() + timedelta(days=30),
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.workspace_subscriptions.insert_one(subscription_doc)

    async def _initialize_workspace_analytics(self, workspace_id: str) -> Dict[str, Any]:
        """Initialize workspace analytics"""
        analytics_doc = {
            "_id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "total_users": 1,
            "active_users": 1,
            "features_used": {},
            "subscription_usage": {},
            "activity_score": 0.0,
            "last_activity": datetime.utcnow(),
            "created_content": 0,
            "generated_leads": 0,
            "email_campaigns": 0,
            "social_posts": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await self.workspace_analytics.insert_one(analytics_doc)
        return analytics_doc

    async def _create_onboarding_flow(self, workspace_id: str, main_goals: List[MainGoal]):
        """Create onboarding flow for workspace"""
        steps = [
            {"step_number": 1, "step_name": "Welcome & Goals", "completed": True},
            {"step_number": 2, "step_name": "Team Setup", "completed": False},
            {"step_number": 3, "step_name": "Branding", "completed": False},
            {"step_number": 4, "step_name": "Feature Configuration", "completed": False},
            {"step_number": 5, "step_name": "Integration Setup", "completed": False},
            {"step_number": 6, "step_name": "Launch", "completed": False}
        ]
        
        onboarding_doc = {
            "_id": str(uuid.uuid4()),
            "workspace_id": workspace_id,
            "current_step": 2,
            "total_steps": 6,
            "completed": False,
            "steps": steps,
            "started_at": datetime.utcnow(),
            "completed_at": None
        }
        
        await self.workspace_onboarding.insert_one(onboarding_doc)

    def _get_default_branding(self) -> Dict[str, Any]:
        """Get default branding settings"""
        return {
            "logo_url": None,
            "primary_color": "#3B82F6",
            "secondary_color": "#1E40AF",
            "accent_color": "#F59E0B",
            "font_family": "Inter",
            "custom_css": None,
            "show_mewayz_branding": True
        }

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default workspace settings"""
        return {
            "timezone": "UTC",
            "language": "en",
            "currency": "USD",
            "date_format": "MM/DD/YYYY",
            "notifications": {
                "email": True,
                "browser": True,
                "mobile": True
            },
            "privacy": {
                "public_profile": False,
                "analytics_sharing": False
            }
        }

    def _get_role_permissions(self, role: WorkspaceRole) -> Dict[str, Any]:
        """Get permissions for workspace role"""
        permissions = {
            WorkspaceRole.OWNER: {
                "manage_workspace": True,
                "manage_billing": True,
                "manage_members": True,
                "manage_content": True,
                "view_analytics": True,
                "delete_workspace": True
            },
            WorkspaceRole.ADMIN: {
                "manage_workspace": True,
                "manage_billing": False,
                "manage_members": True,
                "manage_content": True,
                "view_analytics": True,
                "delete_workspace": False
            },
            WorkspaceRole.EDITOR: {
                "manage_workspace": False,
                "manage_billing": False,
                "manage_members": False,
                "manage_content": True,
                "view_analytics": True,
                "delete_workspace": False
            },
            WorkspaceRole.VIEWER: {
                "manage_workspace": False,
                "manage_billing": False,
                "manage_members": False,
                "manage_content": False,
                "view_analytics": True,
                "delete_workspace": False
            }
        }
        
        return permissions.get(role, permissions[WorkspaceRole.VIEWER])

    def _calculate_monthly_cost(self, plan: SubscriptionPlan, feature_count: int) -> float:
        """Calculate monthly cost based on plan and feature count"""
        if plan == SubscriptionPlan.FREE:
            return 0.0
        elif plan == SubscriptionPlan.PRO:
            return feature_count * 1.0
        elif plan == SubscriptionPlan.ENTERPRISE:
            return feature_count * 1.5
        return 0.0

    def _calculate_yearly_cost(self, plan: SubscriptionPlan, feature_count: int) -> float:
        """Calculate yearly cost based on plan and feature count"""
        if plan == SubscriptionPlan.FREE:
            return 0.0
        elif plan == SubscriptionPlan.PRO:
            return feature_count * 10.0
        elif plan == SubscriptionPlan.ENTERPRISE:
            return feature_count * 15.0
        return 0.0

    async def _send_invitation_email(self, email: str, workspace_name: str, token: str, first_name: str, message: str):
        """Send workspace invitation email"""
        try:
            # This would integrate with your email service
            # For now, we'll just log the invitation
            print(f"Sending invitation email to {email} for workspace {workspace_name}")
            print(f"Invitation token: {token}")
            print(f"Message: {message}")
            
            # TODO: Implement actual email sending with ElasticMail
            
        except Exception as e:
            print(f"Failed to send invitation email: {str(e)}")
            # Don't fail the invitation process if email fails