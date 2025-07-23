"""
Workflow Automation API Endpoints
Sophisticated workflow automation with triggers, actions, and steps
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.database import get_database
from pydantic import BaseModel
import uuid

from core.auth import get_current_user
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from core.auth import get_current_active_user
try:
    from core.workflow_automation_engine import (
        workflow_engine, TriggerType, ActionType, WorkflowStatus
    )
    workflow_engine_available = True
except ImportError:
    workflow_engine = None
    TriggerType = None
    ActionType = None 
    WorkflowStatus = None
    workflow_engine_available = False

try:
    from core.professional_logger import professional_logger, LogLevel, LogCategory
    logger_available = True
except ImportError:
    professional_logger = None
    LogLevel = None
    LogCategory = None
    logger_available = False

router = APIRouter(
    prefix="/api/workflows",
    tags=["Workflow Automation"]
)

# Add a simple working endpoint for AI automation workflows
@router.get("/", response_model=Dict[str, Any])
async def get_workflows_basic(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Basic workflows endpoint for AI automation"""
    try:
        if not workflow_engine_available:
            return {
                "success": True,
                "data": {
                    "workflows": [
                        {
                            "id": "workflow_001",
                            "name": "Email Automation",
                            "status": "active",
                            "created_at": datetime.utcnow().isoformat()
                        }
                    ],
                    "total": 1,
                    "message": "Basic workflow data (engine unavailable)"
                }
            }
        
        # Try to get real workflows
        db = get_database()
        if db:
            user_id = current_user.get("_id") or current_user.get("id")
            workflows = await db.workflows.find({"user_id": user_id}).limit(10).to_list(length=10)
            
            for workflow in workflows:
                workflow["id"] = str(workflow["_id"])
                workflow.pop("_id", None)
            
            return {
                "success": True,
                "data": {
                    "workflows": workflows,
                    "total": len(workflows)
                }
            }
        
        return {
            "success": True,
            "data": {"workflows": [], "total": 0},
            "message": "No workflows found"
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": {"workflows": [], "total": 0},
            "message": f"Error: {str(e)}"
        }

class TriggerConfig(BaseModel):
    type: str  # schedule, event, condition, manual
    config: Dict[str, Any] = {}
    conditions: List[Dict[str, Any]] = []

class ActionConfig(BaseModel):
    type: str  # send_email, send_notification, create_task, update_data, etc.
    config: Dict[str, Any]
    retry_count: int = 3
    timeout_seconds: int = 30

class WorkflowStepConfig(BaseModel):
    name: str
    actions: List[ActionConfig]
    on_success: Optional[str] = None  # Next step ID
    on_failure: Optional[str] = None  # Next step ID
    parallel: bool = False

class CreateWorkflowRequest(BaseModel):
    name: str
    description: str
    trigger: TriggerConfig
    steps: List[WorkflowStepConfig]
    tags: List[str] = []

class ExecuteWorkflowRequest(BaseModel):
    trigger_data: Dict[str, Any] = {}

@router.post("/create", response_model=Dict[str, Any])
async def create_workflow(
    workflow_request: CreateWorkflowRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new workflow
    
    - **name**: Workflow name
    - **description**: Workflow description
    - **trigger**: Trigger configuration (schedule, event, condition, manual)
    - **steps**: List of workflow steps with actions
    - **tags**: Optional tags for organization
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        # Validate trigger type
        try:
            trigger_type = TriggerType(workflow_request.trigger.type)
        except ValueError:
            valid_triggers = [t.value for t in TriggerType]
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid trigger type. Valid types: {', '.join(valid_triggers)}"
            )
        
        # Validate action types
        for step in workflow_request.steps:
            for action in step.actions:
                try:
                    ActionType(action.type)
                except ValueError:
                    valid_actions = [a.value for a in ActionType]
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid action type '{action.type}'. Valid types: {', '.join(valid_actions)}"
                    )
        
        # Convert Pydantic models to dict format for workflow engine
        trigger_config = {
            "type": workflow_request.trigger.type,
            "config": workflow_request.trigger.config,
            "conditions": workflow_request.trigger.conditions
        }
        
        steps_config = []
        for step in workflow_request.steps:
            step_actions = []
            for action in step.actions:
                step_actions.append({
                    "type": action.type,
                    "config": action.config,
                    "retry_count": action.retry_count,
                    "timeout_seconds": action.timeout_seconds
                })
            
            steps_config.append({
                "name": step.name,
                "actions": step_actions,
                "on_success": step.on_success,
                "on_failure": step.on_failure,
                "parallel": step.parallel
            })
        
        # Create workflow
        workflow_id = await workflow_engine.create_workflow(
            name=workflow_request.name,
            description=workflow_request.description,
            user_id=user_id,
            trigger_config=trigger_config,
            steps_config=steps_config,
            tags=workflow_request.tags
        )
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.SYSTEM,
            f"Workflow created: {workflow_request.name}",
            user_id=user_id,
            details={
                "workflow_id": workflow_id,
                "trigger_type": workflow_request.trigger.type,
                "steps_count": len(workflow_request.steps)
            }
        )
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "name": workflow_request.name,
            "message": "Workflow created successfully",
            "created_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to create workflow: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create workflow: {str(e)}"
        )

@router.get("/list", response_model=Dict[str, Any])
async def list_workflows(
    status_filter: Optional[str] = Query(None, description="Filter by workflow status"),
    tag: Optional[str] = Query(None, description="Filter by tag"),
    limit: int = Query(50, description="Maximum workflows to return", ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List workflows for the current user
    
    - **status_filter**: Optional filter by workflow status (active, paused, completed, failed, cancelled)
    - **tag**: Optional filter by tag
    - **limit**: Maximum number of workflows to return (1-100)
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        # Validate status filter
        if status_filter:
            valid_statuses = [s.value for s in WorkflowStatus]
            if status_filter not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status filter. Valid statuses: {', '.join(valid_statuses)}"
                )
        
        # Get workflows from database
        workflows = await workflow_engine.get_user_workflows(user_id)
        
        # Apply filters
        if status_filter:
            workflows = [w for w in workflows if w.get("status") == status_filter]
        
        if tag:
            workflows = [w for w in workflows if tag in w.get("tags", [])]
        
        # Limit results
        workflows = workflows[:limit]
        
        # Calculate summary stats
        total_workflows = len(workflows)
        active_workflows = len([w for w in workflows if w.get("status") == "active"])
        completed_workflows = len([w for w in workflows if w.get("status") == "completed"])
        
        return {
            "success": True,
            "workflows": workflows,
            "total_workflows": total_workflows,
            "active_workflows": active_workflows,
            "completed_workflows": completed_workflows,
            "filters": {
                "status": status_filter,
                "tag": tag,
                "limit": limit
            },
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to list workflows: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workflows: {str(e)}"
        )

@router.get("/stats", response_model=Dict[str, Any])
async def get_workflow_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get workflow statistics for the current user
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        from core.database import get_database
        db = get_database()
        
        # Get workflow counts by status
        status_stats = await db.workflows.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]).to_list(length=None)
        
        # Get total executions
        total_executions = await db.workflow_executions.count_documents({"user_id": user_id})
        successful_executions = await db.workflow_executions.count_documents({
            "user_id": user_id,
            "status": "completed"
        })
        
        # Get recent activity
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_executions = await db.workflow_executions.count_documents({
            "user_id": user_id,
            "started_at": {"$gte": seven_days_ago}
        })
        
        # Calculate success rate
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        # Get active workflow count
        active_workflows = len([w for w in workflow_engine.active_workflows.values() if w.user_id == user_id])
        
        return {
            "success": True,
            "stats": {
                "total_workflows": sum(stat["count"] for stat in status_stats),
                "active_workflows": active_workflows,
                "workflows_by_status": status_stats,
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "success_rate": round(success_rate, 1),
                "recent_executions_7d": recent_executions
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to get workflow stats: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow stats: {str(e)}"
        )

@router.get("/{workflow_id}", response_model=Dict[str, Any])
async def get_workflow(
    workflow_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get a specific workflow by ID
    
    - **workflow_id**: The ID of the workflow to retrieve
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        # Check if workflow exists and belongs to user
        if workflow_id not in workflow_engine.active_workflows:
            # Try to get from database
            from core.database import get_database
            db = get_database()
            
            workflow_data = await db.workflows.find_one({
                "workflow_id": workflow_id,
                "user_id": user_id
            })
            
            if not workflow_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workflow not found"
                )
            
            # Convert str to string and format dates
            workflow_data["_id"] = str(workflow_data["_id"])
            if "created_at" in workflow_data:
                workflow_data["created_at"] = workflow_data["created_at"].isoformat()
            if "updated_at" in workflow_data:
                workflow_data["updated_at"] = workflow_data["updated_at"].isoformat()
            if workflow_data.get("last_run"):
                workflow_data["last_run"] = workflow_data["last_run"].isoformat()
            
            return {
                "success": True,
                "workflow": workflow_data,
                "retrieved_at": datetime.utcnow().isoformat()
            }
        else:
            # Get from active workflows
            workflow = workflow_engine.active_workflows[workflow_id]
            
            if workflow.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this workflow"
                )
            
            workflow_data = {
                "workflow_id": workflow.workflow_id,
                "name": workflow.name,
                "description": workflow.description,
                "user_id": workflow.user_id,
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat(),
                "updated_at": workflow.updated_at.isoformat(),
                "last_run": workflow.last_run.isoformat() if workflow.last_run else None,
                "run_count": workflow.run_count,
                "success_count": workflow.success_count,
                "tags": workflow.tags,
                "trigger": {
                    "trigger_id": workflow.trigger.trigger_id,
                    "type": workflow.trigger.type.value,
                    "config": workflow.trigger.config,
                    "conditions": workflow.trigger.conditions
                },
                "steps": [
                    {
                        "step_id": step.step_id,
                        "name": step.name,
                        "on_success": step.on_success,
                        "on_failure": step.on_failure,
                        "parallel": step.parallel,
                        "actions": [
                            {
                                "action_id": action.action_id,
                                "type": action.type.value,
                                "config": action.config,
                                "retry_count": action.retry_count,
                                "timeout_seconds": action.timeout_seconds
                            }
                            for action in step.actions
                        ]
                    }
                    for step in workflow.steps
                ]
            }
            
            return {
                "success": True,
                "workflow": workflow_data,
                "retrieved_at": datetime.utcnow().isoformat()
            }
        
    except HTTPException:
        raise
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to get workflow: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow: {str(e)}"
        )

@router.post("/{workflow_id}/execute", response_model=Dict[str, Any])
async def execute_workflow(
    workflow_id: str,
    execute_request: ExecuteWorkflowRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Execute a workflow manually
    
    - **workflow_id**: The ID of the workflow to execute
    - **trigger_data**: Optional data to pass to the workflow execution
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        # Check if workflow exists and belongs to user
        if workflow_id in workflow_engine.active_workflows:
            workflow = workflow_engine.active_workflows[workflow_id]
            if workflow.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this workflow"
                )
        else:
            # Check if workflow exists in database
            from core.database import get_database
            db = get_database()
            
            workflow_data = await db.workflows.find_one({
                "workflow_id": workflow_id,
                "user_id": user_id
            })
            
            if not workflow_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workflow not found"
                )
            
            if workflow_data.get("status") != "active":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Workflow is not active and cannot be executed"
                )
        
        # Execute workflow
        execution_id = await workflow_engine.execute_workflow(
            workflow_id=workflow_id,
            trigger_data=execute_request.trigger_data
        )
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.SYSTEM,
            f"Workflow executed manually: {workflow_id}",
            user_id=user_id,
            details={
                "workflow_id": workflow_id,
                "execution_id": execution_id
            }
        )
        
        return {
            "success": True,
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "message": "Workflow execution started",
            "started_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to execute workflow: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute workflow: {str(e)}"
        )

@router.get("/{workflow_id}/executions", response_model=Dict[str, Any])
async def get_workflow_executions(
    workflow_id: str,
    limit: int = Query(20, description="Maximum executions to return", ge=1, le=100),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get execution history for a workflow
    
    - **workflow_id**: The ID of the workflow
    - **limit**: Maximum number of executions to return (1-100)
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        # Verify workflow belongs to user
        from core.database import get_database
        db = get_database()
        
        workflow_data = await db.workflows.find_one({
            "workflow_id": workflow_id,
            "user_id": user_id
        })
        
        if not workflow_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Get executions
        executions = await workflow_engine.get_workflow_executions(workflow_id, limit)
        
        # Calculate execution statistics
        total_executions = len(executions)
        successful_executions = len([e for e in executions if e.get("status") == "completed"])
        failed_executions = len([e for e in executions if e.get("status") == "failed"])
        running_executions = len([e for e in executions if e.get("status") == "active"])
        
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        return {
            "success": True,
            "executions": executions,
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "failed_executions": failed_executions,
            "running_executions": running_executions,
            "success_rate": round(success_rate, 1),
            "workflow_id": workflow_id,
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to get workflow executions: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow executions: {str(e)}"
        )

@router.put("/{workflow_id}/pause", response_model=Dict[str, Any])
async def pause_workflow(
    workflow_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Pause a workflow
    
    - **workflow_id**: The ID of the workflow to pause
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        # Update workflow status in database
        from core.database import get_database
        db = get_database()
        
        result = await db.workflows.update_one(
            {
                "workflow_id": workflow_id,
                "user_id": user_id
            },
            {
                "$set": {
                    "status": WorkflowStatus.PAUSED.value,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Remove from active workflows if present
        if workflow_id in workflow_engine.active_workflows:
            del workflow_engine.active_workflows[workflow_id]
        
        # Cancel scheduled tasks
        if workflow_id in workflow_engine.scheduled_tasks:
            workflow_engine.scheduled_tasks[workflow_id].cancel()
            del workflow_engine.scheduled_tasks[workflow_id]
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.SYSTEM,
            f"Workflow paused: {workflow_id}",
            user_id=user_id,
            details={"workflow_id": workflow_id}
        )
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "message": "Workflow paused successfully",
            "paused_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to pause workflow: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause workflow: {str(e)}"
        )

@router.put("/{workflow_id}/resume", response_model=Dict[str, Any])
async def resume_workflow(
    workflow_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Resume a paused workflow
    
    - **workflow_id**: The ID of the workflow to resume
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        # Update workflow status in database
        from core.database import get_database
        db = get_database()
        
        result = await db.workflows.update_one(
            {
                "workflow_id": workflow_id,
                "user_id": user_id,
                "status": WorkflowStatus.PAUSED.value
            },
            {
                "$set": {
                    "status": WorkflowStatus.ACTIVE.value,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found or not paused"
            )
        
        # Reload workflow into active workflows
        workflow_data = await db.workflows.find_one({
            "workflow_id": workflow_id,
            "user_id": user_id
        })
        
        if workflow_data:
            workflow = workflow_engine._deserialize_workflow(workflow_data)
            workflow_engine.active_workflows[workflow_id] = workflow
            
            # Reschedule if needed
            await workflow_engine._schedule_workflow(workflow)
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.SYSTEM,
            f"Workflow resumed: {workflow_id}",
            user_id=user_id,
            details={"workflow_id": workflow_id}
        )
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "message": "Workflow resumed successfully",
            "resumed_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to resume workflow: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume workflow: {str(e)}"
        )

@router.delete("/{workflow_id}", response_model=Dict[str, Any])
async def delete_workflow(
    workflow_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Delete a workflow
    
    - **workflow_id**: The ID of the workflow to delete
    """
    try:
        user_id = current_user.get("_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user authentication"
            )
        
        # Delete workflow from database
        from core.database import get_database
        db = get_database()
        
        result = await db.workflows.delete_one({
            "workflow_id": workflow_id,
            "user_id": user_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
        
        # Remove from active workflows if present
        if workflow_id in workflow_engine.active_workflows:
            del workflow_engine.active_workflows[workflow_id]
        
        # Cancel scheduled tasks
        if workflow_id in workflow_engine.scheduled_tasks:
            workflow_engine.scheduled_tasks[workflow_id].cancel()
            del workflow_engine.scheduled_tasks[workflow_id]
        
        # Delete related executions
        await db.workflow_executions.delete_many({"workflow_id": workflow_id})
        
        await professional_logger.log(
            LogLevel.INFO, LogCategory.SYSTEM,
            f"Workflow deleted: {workflow_id}",
            user_id=user_id,
            details={"workflow_id": workflow_id}
        )
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "message": "Workflow deleted successfully",
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to delete workflow: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete workflow: {str(e)}"
        )

@router.get("/templates/list", response_model=Dict[str, Any])
async def get_workflow_templates(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get pre-built workflow templates
    """
    try:
        # Define some common workflow templates
        templates = [
            {
                "template_id": "welcome_email",
                "name": "Welcome Email Sequence",
                "description": "Send welcome email to new users and follow up after 3 days",
                "category": "email_marketing",
                "trigger": {
                    "type": "event",
                    "config": {"event_type": "user_registered"}
                },
                "steps": [
                    {
                        "name": "Send Welcome Email",
                        "actions": [
                            {
                                "type": "send_email",
                                "config": {
                                    "to_email": "{user_email}",
                                    "subject": "Welcome to our platform!",
                                    "content": "Welcome {user_name}! Thanks for joining us."
                                }
                            }
                        ]
                    },
                    {
                        "name": "Wait 3 Days",
                        "actions": [
                            {
                                "type": "delay",
                                "config": {"delay_seconds": 259200}  # 3 days
                            }
                        ]
                    },
                    {
                        "name": "Send Follow-up Email",
                        "actions": [
                            {
                                "type": "send_email",
                                "config": {
                                    "to_email": "{user_email}",
                                    "subject": "How's it going?",
                                    "content": "Hi {user_name}, how are you finding our platform?"
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "template_id": "daily_report",
                "name": "Daily Analytics Report",
                "description": "Generate and email daily analytics report",
                "category": "reporting",
                "trigger": {
                    "type": "schedule",
                    "config": {"cron_expression": "0 9 * * *"}  # Daily at 9 AM
                },
                "steps": [
                    {
                        "name": "Generate Report",
                        "actions": [
                            {
                                "type": "generate_report",
                                "config": {
                                    "report_type": "daily_analytics",
                                    "title": "Daily Analytics Report"
                                }
                            }
                        ]
                    },
                    {
                        "name": "Send Report Email",
                        "actions": [
                            {
                                "type": "send_email",
                                "config": {
                                    "to_email": "{user_email}",
                                    "subject": "Daily Analytics Report - {date}",
                                    "content": "Your daily analytics report is ready."
                                }
                            }
                        ]
                    }
                ]
            },
            {
                "template_id": "social_media_post",
                "name": "Scheduled Social Media Post",
                "description": "Post content to multiple social media platforms",
                "category": "social_media",
                "trigger": {
                    "type": "schedule",
                    "config": {"cron_expression": "0 10 * * 1-5"}  # Weekdays at 10 AM
                },
                "steps": [
                    {
                        "name": "Post to Social Media",
                        "actions": [
                            {
                                "type": "social_post",
                                "config": {
                                    "platforms": ["twitter", "linkedin"],
                                    "content": "{post_content}",
                                    "image_url": "{image_url}"
                                }
                            }
                        ]
                    },
                    {
                        "name": "Send Confirmation",
                        "actions": [
                            {
                                "type": "send_notification",
                                "config": {
                                    "title": "Social Media Post Published",
                                    "message": "Your scheduled post has been published",
                                    "channels": ["websocket", "email"]
                                }
                            }
                        ]
                    }
                ]
            }
        ]
        
        return {
            "success": True,
            "templates": templates,
            "total_templates": len(templates),
            "categories": list(set(t["category"] for t in templates)),
            "retrieved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        await professional_logger.log(
            LogLevel.ERROR, LogCategory.SYSTEM,
            f"Failed to get workflow templates: {str(e)}",
            error=e,
            user_id=current_user.get("_id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get workflow templates: {str(e)}"
        )

@router.post("/workflows/create", tags=["AI Workflows"])
async def create_ai_workflow(
    workflow_data: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Create AI-powered workflow"""
    try:
        result = await ai_service.create_ai_workflow_safe(
            user_id=current_user["_id"],
            workflow_data=workflow_data
        )
        
        return {
            "success": True,
            "data": result,
            "message": "AI workflow created successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating AI workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights/generate", tags=["AI Insights"])
async def generate_ai_insights(
    insight_type: str = Body(...),
    parameters: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Generate AI business insights"""
    try:
        result = await ai_service.generate_ai_insights_safe(
            user_id=current_user["_id"],
            insight_type=insight_type,
            parameters=parameters
        )
        
        return {
            "success": True,
            "data": result,
            "message": "AI insights generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating AI insights: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflows", tags=["AI Workflows"])
async def get_user_workflows(
    status: str = Query("active"),
    current_user: dict = Depends(get_current_user)
):
    """Get user's AI workflows"""
    try:
        result = await ai_service.get_user_workflows(
            user_id=current_user["_id"],
            status=status
        )
        
        return {
            "success": True,
            "data": result,
            "message": "User workflows retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Error getting workflows: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
