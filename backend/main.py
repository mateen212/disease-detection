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

# Let's make sure all our important directories are ready to go! 📂
# Think of these as organized folders where we keep different types of files
os.makedirs(Config.UPLOAD_DIR, exist_ok=True)  # Where users upload their files
os.makedirs(Config.DATASET_DIR, exist_ok=True)  # Where we store medical datasets
os.makedirs(Config.MODELS_DIR, exist_ok=True)   # Where our trained AI models live

@asynccontextmanager
async def lifespan(app: FastAPI):
    """This handles what happens when our app starts up and shuts down - 
    think of it as the app's birth and farewell ceremonies! 👋"""
    # Time to wake up and get everything ready! 🌅
    print("🚀 Starting Disease Diagnosis System...")
    
    # Let's set up our database - it's like preparing filing cabinets for patient data! 🗄️
    try:
        create_tables()
        print("✅ Database tables created/verified - Our digital filing system is ready!")
    except Exception as e:
        print(f"❌ Oops! Something went wrong with our database setup: {e}")
    
    # Making sure our AI models have a cozy home to live in! 🏠
    if os.path.exists(Config.MODELS_DIR):
        print("📁 Models directory ready - Our AI brains have a safe place to stay!")
    
    print("🏥 Disease Diagnosis System is ready to help patients!")
    yield
    
    # Time to say goodbye and clean up - thanks for using our system! ✨
    print("👋 Shutting down Disease Diagnosis System - See you next time!")

# Here's where we create the heart of our application! ❤️
# FastAPI is like the receptionist that handles all incoming requests
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

# Let's set up CORS - it's like telling browsers "Hey, it's okay to talk to us!" 🌍
# This makes our API accessible from web browsers safely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In real world, we'd be more picky about who can visit! 🚪
    allow_credentials=True,
    allow_methods=["*"],  # All HTTP methods welcome!
    allow_headers=["*"],  # All headers are friends here!
)

# Time to connect our different parts! It's like introducing departments in a hospital 🏥
app.include_router(predictions.router, prefix="/api/v1", tags=["Predictions"])  # The diagnosis department
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])        # The management office
app.include_router(health.router, prefix="/api/v1", tags=["Health"])          # The system checkup area

# Let's serve our beautiful web pages! 🎨
# This is like having a receptionist show visitors to the right waiting rooms
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Our warm welcome page - like a friendly hospital lobby that greets everyone! 👋"""
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
    """Share some friendly details about our system - like a digital business card! 💼"""
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
    # Time to launch our medical AI assistant! 🚀
    # These lovely messages help everyone know what's happening
    print("🏥 Starting Disease Diagnosis System - Your AI Health Assistant is waking up...")
    print(f"📊 Server will be ready to help at http://{Config.HOST}:{Config.PORT}")
    print("📘 Want to explore our API? Visit: http://localhost:8000/docs")
    print("👤 Patients can access their dashboard at: http://localhost:8000/static/user/index.html")
    print("⚙️ Administrators can manage the system at: http://localhost:8000/static/admin/index.html")
    
    # Let's get this party started! 🎉
    uvicorn.run(
        "main:app",          # Our beautiful application
        host=Config.HOST,    # Where to listen for visitors
        port=Config.PORT,    # Which door to answer
        reload=True,         # Automatically restart when we make changes (like a helpful assistant!)
        log_level="info"     # Keep us informed about what's happening
    )