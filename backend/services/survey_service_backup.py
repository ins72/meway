"""
Survey Service
Business logic for survey and feedback system
"""

import uuid
import logging
logger = logging.getLogger(__name__)
from typing import Dict, List, Optional, Any
from datetime import datetime
from typing import Optional, List, Dict, Any
import json
import csv
import io

from core.database import get_database

class SurveyService:
    """Service class for SurveyService operations"""
    def __init__(self):
        self.db = get_database()

    async def create_survey(self, survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new survey"""
        try:
            # Add metadata
            survey_data.update({
                "id": str(uuid.uuid4()),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active"
            })
            
            # Save to database
            result = await self.db["survey"].insert_one(survey_data)
            
            return {
                "success": True,
                "message": f"Survey created successfully",
                "data": survey_data,
                "id": survey_data["id"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create survey: {str(e)}"
            }

class SurveyService:
    """Service class for SurveyService operations"""
    @staticmethod
    async def get_workspace_surveys(user_id: str) -> Dict[str, Any]:
        """Get all surveys for a user's workspace"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_await collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Get surveys
        surveys_collection = database.surveys
        surveys_cursor = surveys_await collection.find({"workspace_id": str(workspace["_id"])})
        surveys = await surveys_cursor.to_list(length=100)
        
        # Get responses count for each survey
        responses_collection = database.survey_responses
        
        survey_data = []
        for survey in surveys:
            response_count = await responses_await collection.count_documents({"survey_id": survey["_id"]})
            
            # Calculate completion rate and average rating (mock for now)

    async def update_survey(self, survey_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update survey by ID"""
        try:
            # Add update timestamp
            update_data["updated_at"] = datetime.utcnow().isoformat()
            
            result = await self.db["survey"].update_one(
                {"id": survey_id},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                return {
                    "success": False,
                    "error": f"Survey not found"
                }
            
            # Get updated document
            updated_doc = await self.db["survey"].find_one({"id": survey_id})
            updated_doc.pop('_id', None)
            
            return {
                "success": True,
                "message": f"Survey updated successfully",
                "data": updated_doc
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update survey: {str(e)}"
            }

            completion_rate = min(95.0, max(0.0, (response_count * 3.2)))
            average_rating = 4.2 if response_count > 0 else 0
            
            survey_data.append({
                "id": survey["_id"],
                "title": survey["title"],
                "description": survey["description"],
                "status": survey["status"],
                "responses": response_count,
                "completion_rate": completion_rate,
                "average_rating": average_rating,
                "created_at": survey["created_at"].isoformat(),
                "updated_at": survey.get("updated_at", survey["created_at"]).isoformat(),
                "questions": survey["questions"]
            })
        
        analytics = {
            "total_surveys": len(surveys),
            "active_surveys": sum(1 for s in surveys if s["status"] == "active"),
            "total_responses": sum(s["responses"] for s in survey_data),
            "average_completion_rate": sum(s["completion_rate"] for s in survey_data) / len(survey_data) if survey_data else 0
        }
        
        return {
            "surveys": survey_data,
            "analytics": analytics
        }
    
    @staticmethod
    async def create_survey(
        user_id: str,
        title: str,

    async def delete_survey(self, survey_id: str) -> Dict[str, Any]:
        """Delete survey by ID"""
        try:
            result = await self.db["survey"].delete_one({"id": survey_id})
            
            if result.deleted_count == 0:
                return {
                    "success": False,
                    "error": f"Survey not found"
                }
            
            return {
                "success": True,
                "message": f"Survey deleted successfully",
                "deleted_count": result.deleted_count
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete survey: {str(e)}"
            }

        description: str,
        questions: List[Dict[str, Any]],
        settings: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new survey"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_await collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Validate questions
        for question in questions:
            if not question.get("question"):
                raise Exception("Question text is required")
            if not question.get("type"):
                raise Exception("Question type is required")
        
        # Default settings
        default_settings = {
            "allow_anonymous": True,
            "require_email": False,
            "show_progress": True,
            "allow_multiple_submissions": False,
            "collect_ip": False,
            "send_confirmation": False
        }
        default_settings.update(settings)
        
        survey_doc = {
            "_id": str(uuid.uuid4()),
            "workspace_id": str(workspace["_id"]),
            "title": title,
            "description": description,
            "questions": questions,
            "status": "draft",
            "settings": default_settings,
            "created_by": user_id,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        surveys_collection = database.surveys
        await surveys_await collection.insert_one(survey_doc)
        
        return {
            "survey_id": survey_doc["_id"],
            "title": survey_doc["title"],
            "status": "draft",
            "survey_url": f"/surveys/public/{survey_doc['_id']}",
            "embed_code": f'<iframe src="/surveys/embed/{survey_doc["_id"]}" width="100%" height="600" frameborder="0"></iframe>',
            "created_at": survey_doc["created_at"].isoformat()
        }
    
    @staticmethod
    async def get_survey(survey_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific survey"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_await collection.find_one({"owner_id": user_id})
        
        if not workspace:
            return None
        
        # Get survey
        surveys_collection = database.surveys
        survey = await surveys_await collection.find_one({
            "_id": survey_id,
            "workspace_id": str(workspace["_id"])
        })
        
        if not survey:
            return None
        
        # Get response count
        responses_collection = database.survey_responses
        response_count = await responses_await collection.count_documents({"survey_id": survey_id})
        
        return {
            "id": survey["_id"],
            "title": survey["title"],
            "description": survey["description"],
            "questions": survey["questions"],
            "status": survey["status"],
            "settings": survey["settings"],
            "responses": response_count,
            "created_at": survey["created_at"].isoformat(),
            "updated_at": survey.get("updated_at", survey["created_at"]).isoformat()
        }
    
    @staticmethod
    async def update_survey(
        survey_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a survey"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_await collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Update survey
        updates["updated_at"] = datetime.utcnow()
        
        surveys_collection = database.surveys
        result = await surveys_await collection.update_one(
            {"_id": survey_id, "workspace_id": str(workspace["_id"])},
            {"$set": updates}
        )
        
        if result.matched_count == 0:
            raise Exception("Survey not found")
        
        # Return updated survey
        return await SurveyService.get_survey(survey_id, user_id)
    
    @staticmethod
    async def delete_survey(survey_id: str, user_id: str) -> bool:
        """Delete a survey"""
        database = get_database()
        
        # Get user's workspace
        workspaces_collection = database.workspaces
        workspace = await workspaces_await collection.find_one({"owner_id": user_id})
        
        if not workspace:
            raise Exception("Workspace not found")
        
        # Delete survey and its responses
        surveys_collection = database.surveys
        responses_collection = database.survey_responses
        
        # Delete responses first
        await responses_await collection.delete_many({"survey_id": survey_id})
        
        # Delete survey
        result = await surveys_await collection.delete_one({
            "_id": survey_id,
            "workspace_id": str(workspace["_id"])
        })
        
        return result.deleted_count > 0
    
    @staticmethod
    async def submit_response(
        survey_id: str,
        responses: Dict[str, Any],
        respondent_email: Optional[str] = None,
        respondent_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit a response to a survey"""
        database = get_database()
        
        # Get survey
        surveys_collection = database.surveys
        survey = await surveys_await collection.find_one({"_id": survey_id})
        
        if not survey:
            raise Exception("Survey not found")
        
        if survey["status"] != "active":
            raise Exception("Survey is not active")
        
        # Check if multiple submissions are allowed
        responses_collection = database.survey_responses
        
        if not survey["settings"].get("allow_multiple_submissions", False) and respondent_email:
            existing_response = await responses_await collection.find_one({
                "survey_id": survey_id,
                "respondent_email": respondent_email
            })
            if existing_response:
                raise Exception("You have already submitted a response to this survey")
        
        # Validate responses against questions
        question_ids = {q["id"] for q in survey["questions"]}
        response_ids = set(responses.keys())
        
        # Check for required questions
        for question in survey["questions"]:
            if question.get("required", False) and question["id"] not in responses:
                raise Exception(f"Question '{question['question']}' is required")
        
        response_doc = {
            "_id": str(uuid.uuid4()),
            "survey_id": survey_id,
            "responses": responses,
            "respondent_email": respondent_email,
            "respondent_name": respondent_name,
            "submitted_at": datetime.utcnow(),
            "ip_address": None  # Could be populated from request
        }
        
        await responses_await collection.insert_one(response_doc)
        
        return {
            "response_id": response_doc["_id"],
            "submitted_at": response_doc["submitted_at"].isoformat(),
            "message": "Response submitted successfully"
        }
    
    @staticmethod
    async def get_survey_responses(survey_id: str, user_id: str) -> Dict[str, Any]:
        """Get all responses for a survey"""
        database = get_database()
        
        # Verify user owns survey
        survey = await SurveyService.get_survey(survey_id, user_id)
        if not survey:
            raise Exception("Survey not found")
        
        # Get responses
        responses_collection = database.survey_responses
        responses_cursor = responses_await collection.find({"survey_id": survey_id})
        responses = await responses_cursor.to_list(length=1000)
        
        response_data = []
        for response in responses:
            response_data.append({
                "id": response["_id"],
                "responses": response["responses"],
                "respondent_email": response.get("respondent_email"),
                "respondent_name": response.get("respondent_name"),
                "submitted_at": response["submitted_at"].isoformat()
            })
        
        return {
            "survey_id": survey_id,
            "survey_title": survey["title"],
            "total_responses": len(responses),
            "responses": response_data
        }
    
    @staticmethod
    async def get_survey_analytics(survey_id: str, user_id: str) -> Dict[str, Any]:
        """Get analytics for a survey"""
        database = get_database()
        
        # Verify user owns survey
        survey = await SurveyService.get_survey(survey_id, user_id)
        if not survey:
            raise Exception("Survey not found")
        
        # Get responses
        responses_collection = database.survey_responses
        responses_cursor = responses_await collection.find({"survey_id": survey_id})
        responses = await responses_cursor.to_list(length=1000)
        
        # Calculate analytics
        total_responses = len(responses)
        
        # Analyze responses by question
        question_analytics = {}
        for question in survey["questions"]:
            question_id = question["id"]
            question_responses = [r["responses"].get(question_id) for r in responses if question_id in r["responses"]]
            
            analytics = {
                "question": question["question"],
                "type": question["type"],
                "total_responses": len(question_responses),
                "response_rate": (len(question_responses) / total_responses * 100) if total_responses > 0 else 0
            }
            
            # Type-specific analytics
            if question["type"] == "rating":
                numeric_responses = [int(r) for r in question_responses if str(r).isdigit()]
                if numeric_responses:
                    analytics["average_rating"] = sum(numeric_responses) / len(numeric_responses)
                    analytics["rating_distribution"] = {
                        str(i): numeric_responses.count(i) for i in range(1, 6)
                    }
            
            elif question["type"] == "multiple_choice":
                options = question.get("options", [])
                analytics["option_counts"] = {
                    option: question_responses.count(option) for option in options
                }
            
            question_analytics[question_id] = analytics
        
        return {
            "survey_id": survey_id,
            "survey_title": survey["title"],
            "total_responses": total_responses,
            "completion_rate": min(95.0, max(0.0, total_responses * 3.2)),
            "response_timeframe": {
                "first_response": responses[0]["submitted_at"].isoformat() if responses else None,
                "latest_response": responses[-1]["submitted_at"].isoformat() if responses else None
            },
            "question_analytics": question_analytics
        }
    
    @staticmethod
    async def export_responses(survey_id: str, user_id: str, format: str = "csv") -> Dict[str, Any]:
        """Export survey responses"""
        database = get_database()
        
        # Get survey and responses
        responses_data = await SurveyService.get_survey_responses(survey_id, user_id)
        
        if format.lower() == "csv":
            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Get all question IDs for headers
            survey = await SurveyService.get_survey(survey_id, user_id)
            headers = ["Response ID", "Submitted At", "Respondent Email", "Respondent Name"]
            for question in survey["questions"]:
                headers.append(question["question"])
            
            writer.writerow(headers)
            
            # Write responses
            for response in responses_data["responses"]:
                row = [
                    response["id"],
                    response["submitted_at"],
                    response.get("respondent_email", ""),
                    response.get("respondent_name", "")
                ]
                
                for question in survey["questions"]:
                    row.append(response["responses"].get(question["id"], ""))
                
                writer.writerow(row)
            
            csv_content = output.getvalue()
            output.close()
            
            return {
                "format": "csv",
                "filename": f"survey_{survey_id}_responses.csv",
                "content": csv_content,
                "download_url": f"/api/surveys/{survey_id}/export/download?format=csv"
            }
        
        else:
            return responses_data
    
    @staticmethod
    async def get_survey_templates() -> Dict[str, Any]:
        """Get survey templates"""
        templates = [
            {
                "id": "customer_satisfaction",
                "name": "Customer Satisfaction Survey",
                "description": "Measure customer satisfaction with your product or service",
                "category": "feedback",
                "questions": [
                    {
                        "id": "q1",
                        "type": "rating",
                        "question": "How satisfied are you with our product/service?",
                        "scale": "1-5",
                        "required": True
                    },
                    {
                        "id": "q2",
                        "type": "multiple_choice",
                        "question": "How likely are you to recommend us to others?",
                        "options": ["Very likely", "Likely", "Neutral", "Unlikely", "Very unlikely"],
                        "required": True
                    },
                    {
                        "id": "q3",
                        "type": "text",
                        "question": "What can we improve?",
                        "required": False
                    }
                ]
            },
            {
                "id": "event_feedback",
                "name": "Event Feedback Survey",
                "description": "Collect feedback from event attendees",
                "category": "events",
                "questions": [
                    {
                        "id": "q1",
                        "type": "rating",
                        "question": "How would you rate the overall event?",
                        "scale": "1-5",
                        "required": True
                    },
                    {
                        "id": "q2",
                        "type": "multiple_choice",
                        "question": "Which session did you find most valuable?",
                        "options": ["Keynote", "Workshop A", "Workshop B", "Panel Discussion", "Networking"],
                        "required": False
                    },
                    {
                        "id": "q3",
                        "type": "yes_no",
                        "question": "Would you attend our future events?",
                        "required": True
                    }
                ]
            },
            {
                "id": "product_feedback",
                "name": "Product Feature Request",
                "description": "Gather input on new product features",
                "category": "product",
                "questions": [
                    {
                        "id": "q1",
                        "type": "multiple_choice",
                        "question": "Which feature would be most valuable to you?",
                        "options": ["Mobile app", "API access", "Advanced reporting", "Integrations", "AI features"],
                        "required": True
                    },
                    {
                        "id": "q2",
                        "type": "text",
                        "question": "Describe the feature you'd most like to see",
                        "required": False
                    },
                    {
                        "id": "q3",
                        "type": "rating",
                        "question": "How important is this feature to your workflow?",
                        "scale": "1-5",
                        "required": True
                    }
                ]
            }
        ]
        
        return {
            "templates": templates,
            "categories": [
                {"name": "feedback", "count": await collection.count_documents({})},
                {"name": "events", "count": await collection.count_documents({})},
                {"name": "product", "count": await collection.count_documents({})}
            ]
        }

# Global service instance
survey_service = SurveyService()

    async def get_item(self, user_id: str, item_id: str):
        """Get specific item"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            item = await collections['items'].find_one({
                "_id": item_id,
                "user_id": user_id
            })
            
            if not item:
                return {"success": False, "message": "Item not found"}
            
            return {
                "success": True,
                "data": item,
                "message": "Item retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def list_items(self, user_id: str, filters: dict = None, page: int = 1, limit: int = 50):
        """List user's items"""
        try:
            collections = self._get_collections()
            if not collections:
                return {"success": False, "message": "Database unavailable"}
            
            query = {"user_id": user_id}
            if filters:
                query.update(filters)
            
            skip = (page - 1) * limit
            
            cursor = collections['items'].find(query).skip(skip).limit(limit)
            items = await cursor.to_list(length=limit)
            
            total_count = await collections['items'].count_documents(query)
            
            return {
                "success": True,
                "data": {
                    "items": items,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "pages": (total_count + limit - 1) // limit
                    }
                },
                "message": "Items retrieved successfully"
            }
            
        except Exception as e:
            return {"success": False, "message": str(e)}

# Singleton instance
_service_instance = None

def get_survey_service_backup_service():
    """Get singleton instance of SurveyService"""
    global _service_instance
    if _service_instance is None:
        _service_instance = SurveyService()
    return _service_instance