import os
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from backend.predictor import predictor
from backend.universities_data import UNIVERSITIES_DATABASE, CAREER_FIELDS
from backend.resume_parser import ResumeParser

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Predict Your Placement API",
    description="Pro placement intelligence engine powered by Support Vector Regression, automated university benchmarking, and AI resume parsing.",
    version="2.1.0"
)

# Enable CORS for maximum flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class StudentProfile(BaseModel):
    degree_program: str = Field(default="B.Tech", description="Degree program name")
    specialization: str = Field(default="Computer Science", description="Field of study")
    university_tier: str = Field(default="Tier 2", description="University tier: Tier 1, Tier 2, Tier 3")
    university_name: Optional[str] = Field(default="Darshan University", description="Name of student's university")
    university_id: Optional[str] = Field(default="darshan-university", description="University identifier")
    target_field: Optional[str] = Field(default="ai_ml", description="Target favorite career domain")
    cgpa: float = Field(default=8.2, ge=0.0, le=10.0, description="Cumulative Grade Point Average (0-10)")
    backlogs: int = Field(default=0, ge=0, le=20, description="Number of current backlogs")
    num_skills: int = Field(default=8, ge=0, le=30, description="Total technical & soft skills claimed")
    skill_relevance_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Relevance to industry standards (0-1)")
    hackathons_participated: int = Field(default=2, ge=0, le=20, description="Hackathons attended")
    hackathons_won: int = Field(default=1, ge=0, le=10, description="Hackathons won or podium finish")
    certifications_count: int = Field(default=3, ge=0, le=15, description="Industry recognized certifications")
    internships_count: int = Field(default=1, ge=0, le=10, description="Completed internships")
    projects_count: int = Field(default=4, ge=0, le=25, description="Significant portfolio projects")
    communication_score: float = Field(default=75.0, ge=0.0, le=100.0, description="Assessed communication rating (0-100)")
    extracurricular_score: float = Field(default=60.0, ge=0.0, le=100.0, description="Leadership & activities (0-100)")
    university_placement_rate: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Campus historical placement rate")
    university_avg_package_lpa: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="Campus median/avg package LPA")
    resume_score: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="ATS / Content resume quality index")

class PredictRequest(BaseModel):
    profile: StudentProfile
    engine: str = Field(default="svr", description="'svr' for Support Vector Regression, 'gd' for Gradient Descent")
    target_field: Optional[str] = Field(default="ai_ml", description="Favorite target field ID")

class SimulationRequest(BaseModel):
    baseline: StudentProfile
    adjustments: Dict[str, Any]
    target_field: Optional[str] = Field(default="ai_ml", description="Favorite target field ID")

class UniversityDetectRequest(BaseModel):
    query_or_url: str = Field(..., description="University name, domain, or full website URL")

class ResumeParseRequest(BaseModel):
    text: str
    target_field: Optional[str] = "ai_ml"

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Predict Your Placement Engine",
        "model_loaded": True,
        "engine": "Support Vector Regression + Gradient Descent Scratch"
    }

@app.get("/api/universities")
def list_universities():
    """Returns database of global & national universities with placement benchmarks."""
    return UNIVERSITIES_DATABASE

@app.get("/api/universities/search")
def search_universities_endpoint(q: str = ""):
    """
    Returns genuine verified universities matching the search query or empty list if no genuine match.
    """
    return predictor.search_universities(q)

@app.post("/api/university/upload-brochure")
async def upload_university_brochure(file: UploadFile = File(...), university_name: str = Form("My University")):
    """
    Accepts uploaded university placement document or brochure (PDF) and extracts placement rate, criteria, and package.
    """
    try:
        content = await file.read()
        result = predictor.parse_placement_brochure(content, custom_name=university_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process brochure: {str(e)}")

@app.get("/api/career-fields")
def list_career_fields():
    """Returns list of supported career tracks and target domains."""
    return list(CAREER_FIELDS.values())

@app.post("/api/university/detect")
def detect_university_endpoint(req: UniversityDetectRequest):
    """
    Auto-detects university tier, historical placement rate, and placement bar from a URL or name.
    """
    try:
        detected = predictor.detect_university(req.query_or_url)
        return detected
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/resume/parse-file")
async def parse_resume_file(file: UploadFile = File(...), target_field: str = Form("ai_ml")):
    """
    Accepts uploaded PDF/TXT resume and extracts skills, CGPA, projects, internships, and ATS scores.
    """
    try:
        content = await file.read()
        filename = file.filename.lower()
        if filename.endswith(".pdf"):
            text = ResumeParser.extract_text_from_pdf(content)
        else:
            text = content.decode("utf-8", errors="ignore")

        if not text or len(text.strip()) < 20:
            raise HTTPException(status_code=400, detail="Could not extract legible text from file. Please upload a standard text PDF or paste text.")

        parsed = ResumeParser.parse_resume(text, target_field_id=target_field)
        return parsed
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(e)}")

@app.post("/api/resume/parse-text")
def parse_resume_text(req: ResumeParseRequest):
    """
    Parses raw resume text and extracts profile data.
    """
    try:
        parsed = ResumeParser.parse_resume(req.text, target_field_id=req.target_field or "ai_ml")
        return parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict")
def predict_endpoint(req: PredictRequest):
    try:
        profile_dict = req.profile.model_dump()
        target_field_id = req.target_field or req.profile.target_field or "ai_ml"
        result = predictor.predict(profile_dict, engine=req.engine.lower(), target_field_id=target_field_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/simulate")
def simulate_endpoint(req: SimulationRequest):
    try:
        baseline_dict = req.baseline.model_dump()
        target_field_id = req.target_field or "ai_ml"
        result = predictor.simulate_what_if(baseline_dict, req.adjustments, target_field_id=target_field_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/model-info")
def model_info():
    return {
        "metadata": predictor.metadata,
        "gradient_descent": predictor.gd_data["metrics"],
        "architecture": {
            "primary": "Support Vector Regression (SVR)",
            "kernel": "Radial Basis Function (RBF)",
            "hyperparameters": predictor.metadata["svr_metrics"]["params"],
            "comparative": "Batch Gradient Descent (Linear Regressor from Scratch)",
            "scaling": "MinMaxScaler (0, 1)",
            "total_features": len(predictor.feature_columns),
            "feature_columns": predictor.feature_columns
        }
    }

@app.get("/api/dataset-stats")
def dataset_stats():
    return predictor.metadata.get("stats", {})

@app.get("/api/models/benchmark")
def get_model_benchmarks():
    """Returns complete evaluation metrics table for all Task 5 models."""
    return predictor.benchmarks

# Mount frontend directory for static assets
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_frontend():
        index_path = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"message": "Frontend index.html not yet found"}
