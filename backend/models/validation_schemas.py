
# Fixed validation schemas for team management

from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class TeamRole(str, Enum):
    owner = "owner"
    admin = "admin"
    editor = "editor"
    viewer = "viewer"
    member = "member"

class TeamInvitationCreate(BaseModel):
    email: str = Field(..., description="Email address of the person to invite")
    team_id: str = Field(..., description="ID of the team to invite to")
    role: TeamRole = Field(..., description="Role to assign to the invited user")
    message: Optional[str] = Field(None, description="Optional invitation message")

class SocialMediaSearchCriteria(BaseModel):
    hashtags: Optional[List[str]] = Field(None, description="Hashtags to search for")
    location: Optional[str] = Field(None, description="Location filter")
    follower_range: Optional[dict] = Field(None, description="Follower count range")
    engagement_rate_min: Optional[float] = Field(None, description="Minimum engagement rate")
    keywords: Optional[List[str]] = Field(None, description="Keywords to search for")

class VendorOnboardingData(BaseModel):
    business_name: str = Field(..., description="Business name")
    business_type: str = Field(..., description="Type of business")
    contact_email: str = Field(..., description="Contact email")
    phone_number: Optional[str] = Field(None, description="Phone number")
    business_description: str = Field(..., description="Description of business")
    tax_id: Optional[str] = Field(None, description="Tax ID number")
    bank_account_info: Optional[dict] = Field(None, description="Bank account information")
