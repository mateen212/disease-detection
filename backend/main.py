from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import os
import uvicorn
from contextlib import asynccontextmanager

from backend.config import Config
from backend.db.database import create_tables, engine
from backend.routes import predictions, admin, health

# Create directories if they don't exist
os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
os.makedirs(Config.DATASET_DIR, exist_ok=True)
os.makedirs(Config.MODELS_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Disease Diagnosis System...")
    
    # Create database tables
    try:
        create_tables()
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
    
    # Check if models directory exists
    if os.path.exists(Config.MODELS_DIR):
        print("📁 Models directory ready")
    
    print("🏥 Disease Diagnosis System is ready!")
    yield
    
    # Shutdown
    print("👋 Shutting down Disease Diagnosis System...")

# Create FastAPI application
app = FastAPI(
    title="AI-Powered Disease Diagnosis System",
    description="""
    ## AI-Powered Disease Diagnosis System
    
    A comprehensive medical diagnosis system that combines:
    - **Machine Learning** (Random Forest)
    - **Deep Learning** (CNN for skin diseases)
    - **Rule-based reasoning** (Forward chaining)
    - **Neuro-symbolic fusion**
    - **SHAP explainability**
    
    ### Supported Diseases
    
    **Symptom-based:**
    - Dengue
    - COVID-19
    - Pneumonia
    
    **Image-based (Skin diseases):**
    - Melanoma
    - Eczema
    - Psoriasis
    - Acne
    
    ### Features
    - Multi-modal prediction (symptoms + lab values + images)
    - Explainable AI with SHAP
    - Risk level assessment
    - Medical recommendations
    - Prediction history
    - Dataset management
    - Model training
    
    **Note:** This system is for educational and research purposes only. 
    Always consult with healthcare professionals for medical decisions.
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(health.router, prefix="/api/v1", tags=["Health"])

# Serve static files for frontend
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Disease Diagnosis System</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                max-width: 800px; 
                margin: 0 auto; 
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }
            h1 { color: #fff; text-align: center; }
            .card {
                background: rgba(255, 255, 255, 0.2);
                padding: 20px;
                margin: 15px 0;
                border-radius: 10px;
            }
            .button {
                display: inline-block;
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 5px;
            }
            .button:hover { background: #45a049; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 AI-Powered Disease Diagnosis System</h1>
            
            <div class="card">
                <h2>📊 System Information</h2>
                <p><strong>Version:</strong> 1.0.0</p>
                <p><strong>Status:</strong> Running</p>
                <p><strong>Features:</strong> Multi-modal AI Diagnosis, SHAP Explainability, Risk Assessment</p>
            </div>
            
            <div class="card">
                <h2>🔗 Quick Links</h2>
                <a href="/docs" class="button">📘 API Documentation</a>
                <a href="/static/user/index.html" class="button">👤 User Dashboard</a>
                <a href="/static/admin/index.html" class="button">⚙️ Admin Dashboard</a>
                <a href="/api/v1/health" class="button">💓 Health Check</a>
            </div>
            
            <div class="card">
                <h2>🩺 Supported Diagnoses</h2>
                <p><strong>Symptom-based:</strong> Dengue, COVID-19, Pneumonia</p>
                <p><strong>Image-based:</strong> Melanoma, Eczema, Psoriasis, Acne</p>
            </div>
            
            <div class="card">
                <h2>⚠️ Important Note</h2>
                <p>This system is for educational and research purposes only. 
                Always consult with qualified healthcare professionals for medical decisions.</p>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/api/v1/info")
async def get_system_info():
    """Get system information"""
    return {
        "name": "AI-Powered Disease Diagnosis System",
        "version": "1.0.0",
        "description": "Multi-modal AI system for medical diagnosis",
        "supported_diseases": {
            "symptom_based": Config.SYMPTOM_DISEASES,
            "image_based": Config.SKIN_DISEASES
        },
        "features": [
            "Random Forest ML Model",
            "CNN for Image Analysis", 
            "Rule-based Expert System",
            "Neuro-symbolic Fusion",
            "SHAP Explainability",
            "Risk Assessment",
            "Medical Recommendations"
        ],
        "endpoints": {
            "predict": "/api/v1/predict",
            "history": "/api/v1/predictions/{user_id}",
            "upload": "/api/v1/admin/upload-dataset",
            "train": "/api/v1/admin/train-model",
            "health": "/api/v1/health"
        }
    }

if __name__ == "__main__":
    print("🏥 Starting Disease Diagnosis System...")
    print(f"📊 Server will run on http://{Config.HOST}:{Config.PORT}")
    print("📘 API Documentation: http://localhost:8000/docs")
    print("👤 User Dashboard: http://localhost:8000/static/user/index.html")
    print("⚙️ Admin Dashboard: http://localhost:8000/static/admin/index.html")
    
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=True,
        log_level="info"
    )