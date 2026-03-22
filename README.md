# 🏥 AI-Powered Disease Diagnosis System

A comprehensive medical diagnosis system that combines multiple AI approaches for accurate disease prediction and explanation.

## 🔹 System Overview

This system integrates:
- **Random Forest** for symptom-based diagnosis
- **CNN** for skin disease image analysis  
- **Rule-based Expert System** with forward chaining
- **Neuro-symbolic Fusion** for combined predictions
- **SHAP Explainability** for transparent AI decisions

### Supported Diseases

**Symptom-based Diagnosis:**
- Dengue
- COVID-19
- Pneumonia

**Image-based Diagnosis (Skin Diseases):**
- Melanoma
- Eczema
- Psoriasis
- Acne

## 🔹 Features

✅ **Multi-modal Input**: Symptoms, lab values, and medical images  
✅ **Explainable AI**: SHAP-based feature importance and explanations  
✅ **Risk Assessment**: Low/Moderate/High risk classification  
✅ **Medical Recommendations**: Contextual advice based on diagnosis  
✅ **User Dashboard**: Intuitive interface for symptom input and results  
✅ **Admin Dashboard**: Dataset management and model training  
✅ **RESTful API**: FastAPI with comprehensive documentation  
✅ **Data Management**: MySQL database with full history tracking  

## 🔹 Installation & Setup

### Prerequisites

- Python 3.8+
- MySQL 5.7+ or 8.0+
- Node.js (optional, for development)

### 1. Clone Repository

```bash
git clone <repository-url>
cd kbsProject
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

#### Install MySQL

**Windows/macOS:**
Download and install MySQL from [mysql.com](https://dev.mysql.com/downloads/)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install mysql-server
```

#### Create Database

```sql
mysql -u root -p

CREATE DATABASE disease_diagnosis;
CREATE USER 'diagnosis_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON disease_diagnosis.* TO 'diagnosis_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your database credentials
nano .env
```

Update the `.env` file:
```env
DATABASE_URL=mysql+mysqlconnector://diagnosis_user:your_password@localhost:3306/disease_diagnosis
HOST=0.0.0.0
PORT=8000
```

### 6. Initialize Database Tables

```bash
cd backend
python -c "from db.database import create_tables; create_tables()"
```

## 🔹 Running the Application

### Start the Backend Server

```bash
cd backend
python main.py
```

The server will start on `http://localhost:8000`

### Access the Application

- **Main Page**: http://localhost:8000
- **User Dashboard**: http://localhost:8000/static/user/index.html
- **Admin Dashboard**: http://localhost:8000/static/admin/index.html
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## 🔹 Usage Guide

### For Users (Patients)

1. **Access User Dashboard**
   - Open http://localhost:8000/static/user/index.html

2. **Input Patient Information**
   - Enter name, age, and gender
   
3. **Select Symptoms**
   - Check all applicable symptoms from the list
   
4. **Enter Lab Values** (Optional)
   - Platelet count, oxygen saturation, WBC count, temperature
   
5. **Upload Medical Image** (Optional)
   - For skin disease analysis (JPG/PNG, max 10MB)
   
6. **Get Diagnosis**
   - Click "Get AI Diagnosis"
   - View results with:
     - Disease prediction and confidence
     - Risk level assessment
     - Medical explanations
     - Recommendations
     - Probability charts

### For Administrators

1. **Access Admin Dashboard**
   - Open http://localhost:8000/static/admin/index.html

2. **Upload Datasets**
   - Go to "Datasets" tab
   - Upload CSV files for symptom data or ZIP files for images
   - Provide dataset name and description

3. **Train Models**
   - Go to "Model Training" tab
   - Select datasets and model type
   - Start training process
   - Monitor training progress and results

4. **Monitor System**
   - Check "System Status" tab for health monitoring
   - View model status and API endpoints
   - Test system components

## 🔹 API Usage

### Make Prediction

```bash
curl -X POST "http://localhost:8000/api/v1/predict" \
     -H "Content-Type: multipart/form-data" \
     -F "user_name=John Doe" \
     -F "user_age=35" \
     -F "user_gender=Male" \
     -F "symptoms=[\"fever\", \"headache\", \"cough\"]" \
     -F "platelets=120000" \
     -F "oxygen=96" \
     -F "temperature=101.5"
```

### Upload Dataset (Admin)

```bash
curl -X POST "http://localhost:8000/api/v1/admin/upload-dataset" \
     -H "Content-Type: multipart/form-data" \
     -F "name=My Dataset" \
     -F "dataset_type=symptoms" \
     -F "description=Sample medical dataset" \
     -F "file=@dataset.csv"
```

### Train Model (Admin)

```bash
curl -X POST "http://localhost:8000/api/v1/admin/train-model" \
     -H "Content-Type: multipart/form-data" \
     -F "dataset_ids=[1,2]" \
     -F "model_type=random_forest"
```

## 🔹 Project Structure

```
kbsProject/
├── backend/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── db/
│   │   └── database.py         # Database connection and setup
│   ├── models/
│   │   ├── database_models.py  # SQLAlchemy ORM models
│   │   └── pydantic_models.py  # API request/response models
│   ├── routes/
│   │   ├── predictions.py      # Prediction API endpoints
│   │   ├── admin.py           # Admin API endpoints
│   │   └── health.py          # Health check endpoints
│   ├── services/
│   │   └── prediction_service.py # Business logic services
│   └── ml/
│       ├── random_forest_model.py    # Random Forest implementation
│       ├── cnn_model.py              # CNN implementation
│       ├── rule_based_system.py     # Expert system rules
│       ├── shap_explainer.py        # SHAP explanations
│       └── neuro_symbolic_fusion.py # Model fusion logic
├── frontend/
│   ├── user/
│   │   ├── index.html          # User dashboard
│   │   └── user.js             # User dashboard logic
│   └── admin/
│       ├── index.html          # Admin dashboard
│       └── admin.js            # Admin dashboard logic
├── datasets/                   # Uploaded datasets
├── uploads/                    # User file uploads
├── saved_models/              # Trained ML models
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

## 🔹 Model Training

### Sample Data Generation

The system can generate synthetic training data for demonstration:

- **Symptom Data**: Creates realistic patient records with symptoms and lab values
- **Image Data**: Generates synthetic skin condition images for CNN training

### Training Process

1. **Random Forest Training**
   - Uses patient symptoms and lab values
   - Outputs disease probabilities
   - Includes SHAP explainer initialization

2. **CNN Training**
   - Processes skin disease images
   - Uses data augmentation for better generalization
   - Saves trained model for inference

3. **Rule-based System**
   - Pre-defined medical rules for forward chaining
   - No training required, uses expert knowledge

## 🔹 Medical Disclaimer

⚠️ **IMPORTANT MEDICAL DISCLAIMER** ⚠️

This system is designed for **educational and research purposes only**. It should **NOT** be used for actual medical diagnosis or treatment decisions. Always consult qualified healthcare professionals for medical advice, diagnosis, and treatment.

The predictions and recommendations provided by this system are based on AI models and should not replace professional medical judgment.

## 🔹 Development

### Adding New Diseases

1. Update `Config.SYMPTOM_DISEASES` or `Config.SKIN_DISEASES`
2. Add disease-specific rules in `rule_based_system.py`
3. Include disease data in training datasets
4. Update recommendation logic in `neuro_symbolic_fusion.py`

### Managing Multiple Datasets

**📊 Multiple datasets for the same disease are ENCOURAGED!**

- See [MULTIPLE_DATASETS_GUIDE.md](MULTIPLE_DATASETS_GUIDE.md) for detailed guidance
- System automatically combines datasets from different sources
- Improves model accuracy and reduces bias
- Upload datasets from different professors/institutions for better results

### Extending Models

- **New ML Models**: Add to `ml/` directory and integrate in fusion system
- **New Rules**: Extend `Rule` class in rule-based system
- **New Features**: Add feature extraction in model preprocessing

### Database Schema Changes

1. Update SQLAlchemy models in `models/database_models.py`
2. Create database migration scripts
3. Update Pydantic models for API compatibility

## 🔹 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check MySQL service is running
   - Verify credentials in `.env` file
   - Ensure database exists

2. **Model Training Fails**
   - Check dataset format and structure
   - Verify sufficient memory and disk space
   - Check error logs in admin dashboard

3. **File Upload Errors**
   - Verify file size limits (10MB max)
   - Check file format compatibility
   - Ensure upload directories exist and are writable

4. **Performance Issues**
   - Optimize database queries
   - Consider model caching
   - Monitor system resources

### Logs and Monitoring

- Application logs: Check console output
- Training logs: Available in admin dashboard
- Health status: Monitor via `/api/v1/health` endpoint

## 🔹 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## 🔹 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔹 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/docs`
3. Create an issue in the repository
4. Contact the development team

---

**Made with ❤️ for medical AI research and education**