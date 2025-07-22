"""
Workspace Models for Multi-Workspace System
Mewayz v2 - July 22, 2025
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class WorkspaceRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class SubscriptionPlan(str, Enum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class MainGoal(str, Enum):
    INSTAGRAM = "instagram"
    LINK_IN_BIO = "link_in_bio"
    COURSES = "courses"
    ECOMMERCE = "ecommerce"
    CRM = "crm"
    ANALYTICS = "analytics"

class WorkspaceStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    main_goals: List[MainGoal] = Field(default_factory=list)
    subscription_plan: SubscriptionPlan = Field(default=SubscriptionPlan.FREE)
    branding: Optional[Dict[str, Any]] = Field(default_factory=dict)
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict)

class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    industry: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = Field(None, max_length=200)
    main_goals: Optional[List[MainGoal]] = Field(None)
    branding: Optional[Dict[str, Any]] = Field(None)
    settings: Optional[Dict[str, Any]] = Field(None)
    status: Optional[WorkspaceStatus] = Field(None)

class WorkspaceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    industry: Optional[str]
    website: Optional[str]
    main_goals: List[MainGoal]
    subscription_plan: SubscriptionPlan
    branding: Dict[str, Any]
    settings: Dict[str, Any]
    status: WorkspaceStatus
    owner_id: str
    created_at: datetime
    updated_at: datetime
    team_count: int
    features_enabled: List[str]

class WorkspaceMemberInvite(BaseModel):
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    role: WorkspaceRole
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    message: Optional[str] = Field(None, max_length=500)

class WorkspaceMemberUpdate(BaseModel):
    role: Optional[WorkspaceRole] = Field(None)
    status: Optional[str] = Field(None)
    permissions: Optional[Dict[str, Any]] = Field(None)

class WorkspaceMemberResponse(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: WorkspaceRole
    status: str
    permissions: Dict[str, Any]
    invited_at: datetime
    joined_at: Optional[datetime]
    last_active: Optional[datetime]
    invited_by: str

class WorkspaceSubscription(BaseModel):
    workspace_id: str
    plan: SubscriptionPlan
    features_enabled: List[str]
    feature_count: int
    monthly_cost: float
    yearly_cost: float
    billing_cycle: str
    next_billing_date: Optional[datetime]
    payment_method_id: Optional[str]
    stripe_subscription_id: Optional[str]
    
class WorkspaceAnalytics(BaseModel):
    workspace_id: str
    total_users: int
    active_users: int
    features_used: Dict[str, int]
    subscription_usage: Dict[str, Any]
    activity_score: float
    last_activity: datetime
    created_content: int
    generated_leads: int
    email_campaigns: int
    social_posts: int

class OnboardingStep(BaseModel):
    step_number: int
    step_name: str
    completed: bool
    completed_at: Optional[datetime]
    data: Optional[Dict[str, Any]]

class WorkspaceOnboarding(BaseModel):
    workspace_id: str
    current_step: int
    total_steps: int
    completed: bool
    steps: List[OnboardingStep]
    started_at: datetime
    completed_at: Optional[datetime]