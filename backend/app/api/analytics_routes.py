"""
Analytics API Routes - META-MINDS Integration
==============================================

Provides workflow endpoints for META-MINDS analytics
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.workflows.meta_minds_workflow import meta_minds_workflow

router = APIRouter(prefix="/mcp/api/v1/analytics", tags=["META-MINDS Analytics"])


class AnalysisRequest(BaseModel):
    """Request model for META-MINDS analysis"""
    dataset_path: str = Field(..., description="Path to dataset file")
    business_context: str = Field(default="Financial Analysis", description="Business context")
    analysis_focus: str = Field(default="Performance evaluation", description="Analysis focus")
    target_audience: str = Field(default="Executives", description="Target audience")
    num_questions: int = Field(default=15, ge=5, le=30, description="Number of questions")
    auto_save: bool = Field(default=True, description="Auto-save to context")
    generate_report: bool = Field(default=True, description="Generate report file")


class BatchAnalysisRequest(BaseModel):
    """Request model for batch analysis"""
    dataset_paths: List[str] = Field(..., description="List of dataset paths")
    business_context: str = Field(default="Financial Analysis")
    analysis_focus: str = Field(default="Performance evaluation")
    target_audience: str = Field(default="Executives")
    num_questions: int = Field(default=15, ge=5, le=30)


@router.post("/analyze", summary="Run META-MINDS Analysis")
async def run_analysis(request: AnalysisRequest):
    """
    Run complete META-MINDS analysis workflow
    
    Returns:
        - Analysis results with SMART questions
        - Quality assessment metrics
        - Professional report path
        - Context storage confirmation
    """
    
    try:
        result = await meta_minds_workflow.run_full_analysis_workflow(
            dataset_path=request.dataset_path,
            business_context=request.business_context,
            analysis_focus=request.analysis_focus,
            target_audience=request.target_audience,
            num_questions=request.num_questions,
            auto_save=request.auto_save,
            generate_report=request.generate_report
        )
        
        return result
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/batch-analyze", summary="Run Batch META-MINDS Analysis")
async def run_batch_analysis(request: BatchAnalysisRequest, background_tasks: BackgroundTasks):
    """
    Run META-MINDS analysis on multiple datasets
    with cross-dataset comparison
    """
    
    try:
        result = await meta_minds_workflow.batch_analysis_workflow(
            dataset_paths=request.dataset_paths,
            business_context=request.business_context,
            analysis_focus=request.analysis_focus,
            target_audience=request.target_audience,
            num_questions=request.num_questions
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


@router.get("/workflows", summary="List Active Workflows")
async def list_workflows():
    """List all active META-MINDS analysis workflows"""
    
    return {
        "active_workflows": len(meta_minds_workflow.active_analyses),
        "workflows": list(meta_minds_workflow.active_analyses.keys()),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/workflows/{workflow_id}", summary="Get Workflow Status")
async def get_workflow_status(workflow_id: str):
    """Get status of a specific workflow"""
    
    if workflow_id not in meta_minds_workflow.active_analyses:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    
    return meta_minds_workflow.active_analyses[workflow_id]


@router.get("/templates", summary="List Business Context Templates")
async def list_templates():
    """List all available business context templates"""
    
    templates = [
        {
            "id": "financial",
            "name": "Financial Analysis",
            "icon": "💰",
            "focus_areas": ["Performance evaluation", "Risk assessment", "Forecasting"],
            "description": "Financial performance analysis and risk evaluation"
        },
        {
            "id": "sales",
            "name": "Sales Analytics",
            "icon": "📈",
            "focus_areas": ["Sales performance", "Pipeline analysis", "Trend analysis"],
            "description": "Sales performance tracking and pipeline optimization"
        },
        {
            "id": "marketing",
            "name": "Marketing Analytics",
            "icon": "📣",
            "focus_areas": ["Campaign effectiveness", "Customer segmentation", "ROI analysis"],
            "description": "Marketing campaign analysis and customer insights"
        },
        {
            "id": "operations",
            "name": "Operations",
            "icon": "⚙️",
            "focus_areas": ["Efficiency optimization", "Cost reduction", "Process improvement"],
            "description": "Operational efficiency and process optimization"
        },
        {
            "id": "hr",
            "name": "Human Resources",
            "icon": "👥",
            "focus_areas": ["Performance analysis", "Retention studies", "Workforce planning"],
            "description": "HR analytics and workforce optimization"
        },
        {
            "id": "customer",
            "name": "Customer Analytics",
            "icon": "🎯",
            "focus_areas": ["Behavior analysis", "Satisfaction studies", "Churn prediction"],
            "description": "Customer behavior and satisfaction analysis"
        },
        {
            "id": "product",
            "name": "Product Analytics",
            "icon": "📦",
            "focus_areas": ["Usage analysis", "Feature adoption", "Performance metrics"],
            "description": "Product usage and performance analysis"
        }
    ]
    
    return {"templates": templates, "total": len(templates)}

