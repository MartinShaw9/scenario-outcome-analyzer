#!/usr/bin/env python3
"""
FastAPI Server for Scenario Outcome Analyzer
REST API for programmatic access
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime
import asyncio
from scenario_analyzer import ScenarioAnalyzer, ScenarioAnalysis, Outcome

# FastAPI app
app = FastAPI(
    title="Scenario Outcome Analyzer API",
    description="AI-powered scenario analysis and outcome prediction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (use database in production)
analysis_store = {}
analyzer_instances = {}

# Pydantic models
class AnalysisRequest(BaseModel):
    situation: str = Field(..., description="Description of the situation to analyze")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context information")
    api_key: Optional[str] = Field(None, description="OpenAI API key for AI analysis")
    model: str = Field("gpt-4", description="AI model to use")
    
class OutcomeResponse(BaseModel):
    description: str
    probability: float
    impact_level: str
    risk_factors: List[str]
    opportunities: List[str]
    timeline: str
    confidence_score: float

class AnalysisResponse(BaseModel):
    analysis_id: str
    situation: str
    context_factors: List[str]
    outcomes: List[OutcomeResponse]
    key_variables: List[str]
    recommendations: List[str]
    analysis_timestamp: str
    status: str

class AnalysisStatus(BaseModel):
    analysis_id: str
    status: str
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None

# Helper functions
def convert_outcome_to_response(outcome: Outcome) -> OutcomeResponse:
    """Convert Outcome object to OutcomeResponse"""
    return OutcomeResponse(
        description=outcome.description,
        probability=outcome.probability,
        impact_level=outcome.impact_level,
        risk_factors=outcome.risk_factors,
        opportunities=outcome.opportunities,
        timeline=outcome.timeline,
        confidence_score=outcome.confidence_score
    )

def convert_analysis_to_response(analysis: ScenarioAnalysis, analysis_id: str) -> AnalysisResponse:
    """Convert ScenarioAnalysis to AnalysisResponse"""
    return AnalysisResponse(
        analysis_id=analysis_id,
        situation=analysis.situation,
        context_factors=analysis.context_factors,
        outcomes=[convert_outcome_to_response(outcome) for outcome in analysis.outcomes],
        key_variables=analysis.key_variables,
        recommendations=analysis.recommendations,
        analysis_timestamp=analysis.analysis_timestamp,
        status="completed"
    )

async def perform_analysis(analysis_id: str, request: AnalysisRequest):
    """Perform analysis in background"""
    try:
        # Update status
        analysis_store[analysis_id]["status"] = "processing"
        
        # Initialize analyzer
        analyzer = ScenarioAnalyzer(
            api_key=request.api_key,
            model=request.model
        )
        
        # Perform analysis
        analysis = analyzer.analyze(request.situation, request.context)
        
        # Store results
        analysis_store[analysis_id].update({
            "status": "completed",
            "analysis": analysis,
            "completed_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        analysis_store[analysis_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Scenario Outcome Analyzer API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_analyses": len([a for a in analysis_store.values() if a["status"] == "processing"])
    }

@app.post("/analyze", response_model=AnalysisStatus)
async def create_analysis(request: AnalysisRequest, background_tasks: BackgroundTasks):
    """Create new scenario analysis"""
    
    # Generate unique ID
    analysis_id = str(uuid.uuid4())
    
    # Initialize analysis record
    analysis_store[analysis_id] = {
        "analysis_id": analysis_id,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "request": request.dict(),
        "analysis": None,
        "completed_at": None,
        "error": None
    }
    
    # Start background analysis
    background_tasks.add_task(perform_analysis, analysis_id, request)
    
    return AnalysisStatus(
        analysis_id=analysis_id,
        status="queued",
        created_at=analysis_store[analysis_id]["created_at"]
    )

@app.get("/analyze/{analysis_id}/status", response_model=AnalysisStatus)
async def get_analysis_status(analysis_id: str):
    """Get analysis status"""
    
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    record = analysis_store[analysis_id]
    
    return AnalysisStatus(
        analysis_id=analysis_id,
        status=record["status"],
        created_at=record["created_at"],
        completed_at=record.get("completed_at"),
        error=record.get("error")
    )

@app.get("/analyze/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_result(analysis_id: str):
    """Get analysis results"""
    
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    record = analysis_store[analysis_id]
    
    if record["status"] != "completed":
        raise HTTPException(
            status_code=400, 
            detail=f"Analysis not completed. Status: {record['status']}"
        )
    
    if record["analysis"] is None:
        raise HTTPException(status_code=500, detail="Analysis data not available")
    
    return convert_analysis_to_response(record["analysis"], analysis_id)

@app.post("/analyze/sync", response_model=AnalysisResponse)
async def analyze_sync(request: AnalysisRequest):
    """Synchronous analysis (blocks until complete)"""
    
    try:
        # Initialize analyzer
        analyzer = ScenarioAnalyzer(
            api_key=request.api_key,
            model=request.model
        )
        
        # Perform analysis
        analysis = analyzer.analyze(request.situation, request.context)
        
        # Generate ID and return
        analysis_id = str(uuid.uuid4())
        return convert_analysis_to_response(analysis, analysis_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/analyze", response_model=List[AnalysisStatus])
async def list_analyses(limit: int = 10, status: Optional[str] = None):
    """List recent analyses"""
    
    analyses = list(analysis_store.values())
    
    # Filter by status if provided
    if status:
        analyses = [a for a in analyses if a["status"] == status]
    
    # Sort by creation time (newest first)
    analyses.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Limit results
    analyses = analyses[:limit]
    
    return [
        AnalysisStatus(
            analysis_id=a["analysis_id"],
            status=a["status"],
            created_at=a["created_at"],
            completed_at=a.get("completed_at"),
            error=a.get("error")
        )
        for a in analyses
    ]

@app.delete("/analyze/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete analysis"""
    
    if analysis_id not in analysis_store:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    del analysis_store[analysis_id]
    
    return {"message": "Analysis deleted successfully"}

@app.get("/models")
async def list_models():
    """List available AI models"""
    return {
        "models": [
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "description": "Most capable model for complex analysis"
            },
            {
                "id": "gpt-4-turbo",
                "name": "GPT-4 Turbo",
                "description": "Faster GPT-4 variant"
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo",
                "description": "Fast and cost-effective"
            },
            {
                "id": "rule-based",
                "name": "Rule-based",
                "description": "No API key required, basic analysis"
            }
        ]
    }

@app.get("/examples")
async def get_examples():
    """Get example scenarios"""
    return {
        "examples": [
            {
                "title": "Business Launch",
                "situation": "I'm considering launching a new AI-powered mobile app for small businesses in India. The app would help with inventory management and customer analytics. I have a team of 3 developers and $50,000 in funding.",
                "context": {
                    "industry": "Technology",
                    "timeline": "Medium-term",
                    "budget": "Medium",
                    "risk_tolerance": "Moderate"
                }
            },
            {
                "title": "Career Change",
                "situation": "I'm a software engineer with 5 years experience considering switching to data science. I have basic Python knowledge but no formal ML training. The job market seems competitive.",
                "context": {
                    "industry": "Technology",
                    "timeline": "Long-term",
                    "risk_tolerance": "Conservative"
                }
            },
            {
                "title": "Investment Decision",
                "situation": "I have $100,000 to invest and am considering between real estate, stock market, or starting a franchise business. I'm 35 years old with moderate risk tolerance.",
                "context": {
                    "industry": "Finance",
                    "timeline": "Long-term",
                    "budget": "High",
                    "risk_tolerance": "Moderate"
                }
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)