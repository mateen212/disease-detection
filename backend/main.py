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
    """Professional landing page with authentication - like a modern hospital reception! 🏥"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>HealthAI - Professional Medical Diagnosis System</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: white;
                color: #2d3748;
                line-height: 1.6;
            }
            
            .header {
                background: white;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                padding: 1rem 0;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                z-index: 100;
            }
            
            .header-content {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 2rem;
            }
            
            .logo {
                display: flex;
                align-items: center;
                gap: 12px;
                font-size: 1.5rem;
                font-weight: 700;
                color: #667eea;
                text-decoration: none;
            }
            
            .auth-buttons {
                display: flex;
                gap: 1rem;
            }
            
            .btn {
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 600;
                text-decoration: none;
                transition: all 0.3s ease;
                border: none;
                cursor: pointer;
                font-size: 14px;
            }
            
            .btn-outline {
                background: transparent;
                color: #667eea;
                border: 2px solid #667eea;
            }
            
            .btn-outline:hover {
                background: #667eea;
                color: white;
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
            }
            
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            }
            
            .hero {
                padding: 120px 0 80px;
                text-align: center;
            }
            
            .hero-content {
                max-width: 800px;
                margin: 0 auto;
                padding: 0 2rem;
            }
            
            .hero h1 {
                font-size: 3.5rem;
                font-weight: 700;
                color: #2d3748;
                margin-bottom: 1.5rem;
                line-height: 1.2;
            }
            
            .hero p {
                font-size: 1.25rem;
                color: #718096;
                margin-bottom: 2.5rem;
            }
            
            .features {
                padding: 80px 0;
                background: #f8fafc;
            }
            
            .features-content {
                max-width: 1200px;
                margin: 0 auto;
                padding: 0 2rem;
            }
            
            .features h2 {
                text-align: center;
                font-size: 2.5rem;
                font-weight: 700;
                color: #2d3748;
                margin-bottom: 3rem;
            }
            
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 2rem;
            }
            
            .feature-card {
                background: white;
                padding: 2rem;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.08);
                text-align: center;
                transition: transform 0.3s ease;
            }
            
            .feature-card:hover {
                transform: translateY(-8px);
            }
            
            .feature-icon {
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 1.5rem;
                color: white;
                font-size: 2rem;
            }
            
            .feature-card h3 {
                font-size: 1.5rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 1rem;
            }
            
            .feature-card p {
                color: #718096;
            }
            
            .cta {
                padding: 80px 0;
                text-align: center;
            }
            
            .cta-content {
                max-width: 600px;
                margin: 0 auto;
                padding: 0 2rem;
            }
            
            .cta h2 {
                font-size: 2.5rem;
                font-weight: 700;
                color: #2d3748;
                margin-bottom: 1.5rem;
            }
            
            .cta p {
                font-size: 1.1rem;
                color: #718096;
                margin-bottom: 2rem;
            }
            
            .footer {
                background: #2d3748;
                color: white;
                padding: 2rem 0;
                text-align: center;
            }
            
            .footer p {
                color: #a0aec0;
            }
            
            @media (max-width: 768px) {
                .hero h1 {
                    font-size: 2.5rem;
                }
                
                .auth-buttons {
                    flex-direction: column;
                    gap: 0.5rem;
                }
            }
        </style>
    </head>
    <body>
        <header class="header">
            <div class="header-content">
                <a href="/" class="logo">
                    <i class="fas fa-heartbeat"></i>
                    HealthAI
                </a>
                <div class="auth-buttons">
                    <a href="/login" class="btn btn-outline">
                        <i class="fas fa-sign-in-alt"></i> Sign In
                    </a>
                    <a href="/register" class="btn btn-primary">
                        <i class="fas fa-user-plus"></i> Get Started
                    </a>
                </div>
            </div>
        </header>
        
        <main>
            <section class="hero">
                <div class="hero-content">
                    <h1>AI-Powered Medical Diagnosis</h1>
                    <p>Professional healthcare insights powered by advanced machine learning, providing accurate disease diagnosis and risk assessment for medical professionals and patients.</p>
                    <div style="display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap;">
                        <a href="/register" class="btn btn-primary" style="font-size: 1.1rem; padding: 16px 32px;">
                            <i class="fas fa-rocket"></i> Start Diagnosis
                        </a>
                        <a href="/docs" class="btn btn-outline" style="font-size: 1.1rem; padding: 16px 32px;">
                            <i class="fas fa-book"></i> View Documentation
                        </a>
                    </div>
                </div>
            </section>
            
            <section class="features">
                <div class="features-content">
                    <h2>Advanced Medical AI Features</h2>
                    <div class="features-grid">
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-brain"></i>
                            </div>
                            <h3>Multi-Modal AI</h3>
                            <p>Combines symptom analysis, lab values, and medical imaging for comprehensive diagnosis using Random Forest and CNN models.</p>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-shield-alt"></i>
                            </div>
                            <h3>Risk Assessment</h3>
                            <p>Intelligent risk level classification with detailed explanations and medical recommendations for immediate action.</p>
                        </div>
                        
                        <div class="feature-card">
                            <div class="feature-icon">
                                <i class="fas fa-microscope"></i>
                            </div>
                            <h3>Explainable AI</h3>
                            <p>SHAP-powered explanations showing exactly why the AI made each diagnosis, building trust and understanding.</p>
                        </div>
                    </div>
                </div>
            </section>
            
            <section class="cta">
                <div class="cta-content">
                    <h2>Ready to Get Started?</h2>
                    <p>Join healthcare professionals already using our AI system for better patient outcomes.</p>
                    <a href="/register" class="btn btn-primary" style="font-size: 1.2rem; padding: 18px 36px;">
                        <i class="fas fa-user-md"></i> Create Account
                    </a>
                </div>
            </section>
        </main>
        
        <footer class="footer">
            <p>&copy; 2026 HealthAI. Professional Medical AI System - For educational and research purposes.</p>
        </footer>
    </body>
    </html>
    """

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Professional login page for accessing the medical AI system 🔐"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sign In - HealthAI</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: white;
                color: #2d3748;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 2rem;
            }
            
            .login-container {
                background: white;
                padding: 3rem;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 450px;
                position: relative;
            }
            
            .login-header {
                text-align: center;
                margin-bottom: 2.5rem;
            }
            
            .logo {
                display: inline-flex;
                align-items: center;
                gap: 12px;
                font-size: 2rem;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 1rem;
                text-decoration: none;
            }
            
            .login-title {
                font-size: 1.75rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 0.5rem;
            }
            
            .login-subtitle {
                color: #718096;
                font-size: 1rem;
            }
            
            .form-group {
                margin-bottom: 1.5rem;
            }
            
            .form-label {
                display: block;
                font-weight: 500;
                color: #4a5568;
                margin-bottom: 0.5rem;
                font-size: 0.9rem;
            }
            
            .form-input {
                width: 100%;
                padding: 1rem 1.25rem;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 1rem;
                transition: all 0.3s ease;
                background: #f8fafc;
            }
            
            .form-input:focus {
                outline: none;
                border-color: #667eea;
                background: white;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .form-input-icon {
                position: relative;
            }
            
            .form-input-icon i {
                position: absolute;
                left: 1rem;
                top: 50%;
                transform: translateY(-50%);
                color: #a0aec0;
            }
            
            .form-input-icon input {
                padding-left: 3rem;
            }
            
            .btn-login {
                width: 100%;
                padding: 1rem 1.5rem;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-bottom: 1.5rem;
            }
            
            .btn-login:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            }
            
            .form-footer {
                text-align: center;
                padding-top: 1.5rem;
                border-top: 1px solid #e2e8f0;
            }
            
            .form-footer a {
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
            }
            
            .form-footer a:hover {
                text-decoration: underline;
            }
            
            .back-link {
                position: absolute;
                top: 1rem;
                left: 1rem;
                color: #718096;
                text-decoration: none;
                font-size: 0.9rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .back-link:hover {
                color: #667eea;
            }
            
            .role-selector {
                display: flex;
                gap: 0.5rem;
                margin-bottom: 1.5rem;
            }
            
            .role-option {
                flex: 1;
                padding: 0.75rem;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
                font-weight: 500;
            }
            
            .role-option:hover {
                border-color: #667eea;
            }
            
            .role-option.active {
                background: #667eea;
                color: white;
                border-color: #667eea;
            }
        </style>
    </head>
    <body>
        <div class="login-container">
            <a href="/" class="back-link">
                <i class="fas fa-arrow-left"></i>
                Back to Home
            </a>
            
            <div class="login-header">
                <a href="/" class="logo">
                    <i class="fas fa-heartbeat"></i>
                    HealthAI
                </a>
                <h1 class="login-title">Welcome Back</h1>
                <p class="login-subtitle">Sign in to access your medical AI dashboard</p>
            </div>
            
            <form id="loginForm" onsubmit="handleLogin(event)">
                <div class="form-group">
                    <label class="form-label">Account Type</label>
                    <div class="role-selector">
                        <div class="role-option active" onclick="selectRole('user', this)">
                            <i class="fas fa-user"></i> Patient
                        </div>
                        <div class="role-option" onclick="selectRole('admin', this)">
                            <i class="fas fa-user-md"></i> Medical Staff
                        </div>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="email" class="form-label">Email Address</label>
                    <div class="form-input-icon">
                        <i class="fas fa-envelope"></i>
                        <input type="email" id="email" class="form-input" placeholder="Enter your email" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="password" class="form-label">Password</label>
                    <div class="form-input-icon">
                        <i class="fas fa-lock"></i>
                        <input type="password" id="password" class="form-input" placeholder="Enter your password" required>
                    </div>
                </div>
                
                <button type="submit" class="btn-login">
                    <i class="fas fa-sign-in-alt"></i> Sign In
                </button>
            </form>
            
            <div class="form-footer">
                <p>Don't have an account? <a href="/register">Create one here</a></p>
            </div>
        </div>
        
        <script>
            let selectedRole = 'user'; // Default role
            
            function selectRole(role, element) {
                selectedRole = role;
                document.querySelectorAll('.role-option').forEach(el => el.classList.remove('active'));
                element.classList.add('active');
            }
            
            function handleLogin(event) {
                event.preventDefault();
                
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                
                // Simple demo authentication
                if (email && password) {
                    // Store user info in localStorage for demo purposes
                    localStorage.setItem('user', JSON.stringify({
                        email: email,
                        role: selectedRole,
                        name: email.split('@')[0],
                        loggedIn: true
                    }));
                    
                    // Redirect based on role
                    if (selectedRole === 'admin') {
                        window.location.href = '/static/admin/index.html';
                    } else {
                        window.location.href = '/static/user/index.html';
                    }
                } else {
                    alert('Please fill in all fields');
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/register", response_class=HTMLResponse) 
async def register_page():
    """Professional registration page for new users to join our medical AI system 📝"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Create Account - HealthAI</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: white;
                color: #2d3748;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 2rem;
            }
            
            .register-container {
                background: white;
                padding: 3rem;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 500px;
                position: relative;
            }
            
            .register-header {
                text-align: center;
                margin-bottom: 2.5rem;
            }
            
            .logo {
                display: inline-flex;
                align-items: center;
                gap: 12px;
                font-size: 2rem;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 1rem;
                text-decoration: none;
            }
            
            .register-title {
                font-size: 1.75rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 0.5rem;
            }
            
            .register-subtitle {
                color: #718096;
                font-size: 1rem;
            }
            
            .form-group {
                margin-bottom: 1.5rem;
            }
            
            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1rem;
            }
            
            .form-label {
                display: block;
                font-weight: 500;
                color: #4a5568;
                margin-bottom: 0.5rem;
                font-size: 0.9rem;
            }
            
            .form-input, .form-select {
                width: 100%;
                padding: 1rem 1.25rem;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
                font-size: 1rem;
                transition: all 0.3s ease;
                background: #f8fafc;
            }
            
            .form-input:focus, .form-select:focus {
                outline: none;
                border-color: #667eea;
                background: white;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            
            .form-input-icon {
                position: relative;
            }
            
            .form-input-icon i {
                position: absolute;
                left: 1rem;
                top: 50%;
                transform: translateY(-50%);
                color: #a0aec0;
            }
            
            .form-input-icon input {
                padding-left: 3rem;
            }
            
            .btn-register {
                width: 100%;
                padding: 1rem 1.5rem;
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-bottom: 1.5rem;
            }
            
            .btn-register:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
            }
            
            .form-footer {
                text-align: center;
                padding-top: 1.5rem;
                border-top: 1px solid #e2e8f0;
            }
            
            .form-footer a {
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
            }
            
            .form-footer a:hover {
                text-decoration: underline;
            }
            
            .back-link {
                position: absolute;
                top: 1rem;
                left: 1rem;
                color: #718096;
                text-decoration: none;
                font-size: 0.9rem;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            
            .back-link:hover {
                color: #667eea;
            }
            
            .role-selector {
                display: flex;
                gap: 0.5rem;
                margin-bottom: 1.5rem;
            }
            
            .role-option {
                flex: 1;
                padding: 0.75rem;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 0.9rem;
                font-weight: 500;
            }
            
            .role-option:hover {
                border-color: #667eea;
            }
            
            .role-option.active {
                background: #667eea;
                color: white;
                border-color: #667eea;
            }
            
            @media (max-width: 768px) {
                .form-row {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="register-container">
            <a href="/" class="back-link">
                <i class="fas fa-arrow-left"></i>
                Back to Home
            </a>
            
            <div class="register-header">
                <a href="/" class="logo">
                    <i class="fas fa-heartbeat"></i>
                    HealthAI
                </a>
                <h1 class="register-title">Create Account</h1>
                <p class="register-subtitle">Join our professional medical AI platform</p>
            </div>
            
            <form id="registerForm" onsubmit="handleRegister(event)">
                <div class="form-group">
                    <label class="form-label">I am a...</label>
                    <div class="role-selector">
                        <div class="role-option active" onclick="selectRole('user', this)">
                            <i class="fas fa-user"></i> Patient
                        </div>
                        <div class="role-option" onclick="selectRole('admin', this)">
                            <i class="fas fa-user-md"></i> Medical Professional
                        </div>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="firstName" class="form-label">First Name</label>
                        <input type="text" id="firstName" class="form-input" placeholder="John" required>
                    </div>
                    <div class="form-group">
                        <label for="lastName" class="form-label">Last Name</label>
                        <input type="text" id="lastName" class="form-input" placeholder="Doe" required>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="email" class="form-label">Email Address</label>
                    <div class="form-input-icon">
                        <i class="fas fa-envelope"></i>
                        <input type="email" id="email" class="form-input" placeholder="john.doe@example.com" required>
                    </div>
                </div>
                
                <div class="form-row">
                    <div class="form-group">
                        <label for="age" class="form-label">Age</label>
                        <input type="number" id="age" class="form-input" placeholder="30" min="1" max="120" required>
                    </div>
                    <div class="form-group">
                        <label for="gender" class="form-label">Gender</label>
                        <select id="gender" class="form-select" required>
                            <option value="">Select Gender</option>
                            <option value="male">Male</option>
                            <option value="female">Female</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="password" class="form-label">Password</label>
                    <div class="form-input-icon">
                        <i class="fas fa-lock"></i>
                        <input type="password" id="password" class="form-input" placeholder="Create a secure password" required>
                    </div>
                </div>
                
                <button type="submit" class="btn-register">
                    <i class="fas fa-user-plus"></i> Create Account
                </button>
            </form>
            
            <div class="form-footer">
                <p>Already have an account? <a href="/login">Sign in here</a></p>
            </div>
        </div>
        
        <script>
            let selectedRole = 'user'; // Default role
            
            function selectRole(role, element) {
                selectedRole = role;
                document.querySelectorAll('.role-option').forEach(el => el.classList.remove('active'));
                element.classList.add('active');
            }
            
            function handleRegister(event) {
                event.preventDefault();
                
                const firstName = document.getElementById('firstName').value;
                const lastName = document.getElementById('lastName').value;
                const email = document.getElementById('email').value;
                const age = document.getElementById('age').value;
                const gender = document.getElementById('gender').value;
                const password = document.getElementById('password').value;
                
                // Simple validation
                if (!firstName || !lastName || !email || !age || !gender || !password) {
                    alert('Please fill in all fields');
                    return;
                }
                
                // Store user info in localStorage for demo purposes
                const userData = {
                    firstName: firstName,
                    lastName: lastName,
                    name: `${firstName} ${lastName}`,
                    email: email,
                    age: parseInt(age),
                    gender: gender,
                    role: selectedRole,
                    loggedIn: true
                };
                
                localStorage.setItem('user', JSON.stringify(userData));
                
                // Redirect based on role
                if (selectedRole === 'admin') {
                    window.location.href = '/static/admin/index.html';
                } else {
                    window.location.href = '/static/user/index.html';
                }
            }
        </script>
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