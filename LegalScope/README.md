# Legal Contract Analyzer

An **AI-powered legal contract analysis tool** that combines specialized NLP models with Large Language Models (LLMs) to provide comprehensive contract insights. Upload legal contracts and get automated clause extraction, risk detection, legal insights, and actionable recommendations.

## 🚀 **Key Features**

### **Document Processing**
- **Multi-format Support**: PDF, DOCX, DOC, TXT files
- **Intelligent Text Extraction**: Handles complex document layouts
- **File Validation**: Size and format compatibility checks

### **AI-Powered Analysis**
- **Clause Extraction & Classification**: Identifies 15+ contract clause types
- **Smart Summarization**: Converts legal jargon into plain language
- **Risk Detection**: Flags potential legal and business risks
- **LLM Legal Insights**: Advanced analysis using OpenAI GPT-4

### **Comprehensive Reporting**
- **Overall Summary**: High-level contract overview
- **Clause Analysis**: Individual summaries with confidence scores
- **Risk Assessment**: Severity levels with mitigation strategies
- **Legal Recommendations**: Actionable negotiation points
- **Compliance Check**: Regulatory and industry compliance assessment

## 🎯 **Use Cases**

### **For Business Users**
- **Contract Review**: Quickly understand complex legal documents
- **Risk Assessment**: Identify potential issues before signing
- **Negotiation Support**: Know what terms to negotiate
- **Compliance Check**: Ensure regulatory requirements are met

### **For Legal Professionals**
- **Document Analysis**: Speed up contract review process
- **Risk Identification**: Automated risk detection
- **Client Communication**: Generate plain-language explanations
- **Due Diligence**: Comprehensive contract assessment

## 🏗️ **Technology Stack**

### **Backend**
- **Python 3.11** with Flask web framework
- **Hugging Face Transformers** for specialized NLP models
- **PyTorch** for AI model inference
- **pdfplumber** for PDF text extraction
- **python-docx** for DOCX processing

### **AI Models**
- **BART-large-CNN**: Document and clause summarization
- **BART-large-MNLI**: Zero-shot clause classification
- **RoBERTa**: Sentiment analysis for risk detection
- **OpenAI GPT-4**: Advanced legal insights and recommendations

### **Frontend**
- **Bootstrap 5** for responsive design
- **Modern JavaScript** for interactive features
- **Professional CSS** styling

## 📦 **Installation**

### **Prerequisites**
- Python 3.8 or higher
- pip (Python package installer)
- Git

### **Quick Setup**

1. **Clone the repository**:
```bash
git clone <repository-url>
cd LegalScope
```

2. **Create virtual environment**:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
# Copy environment template
cp env_example.txt .env

# Edit .env with your configuration
# For LLM features, add your OpenAI API key
```

5. **Create necessary directories**:
```bash
mkdir uploads logs
```

## ⚙️ **Configuration**

### **Environment Variables**

Create a `.env` file with the following settings:

```bash
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# LLM Configuration (Optional but recommended)
ENABLE_LLM=true
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
OPENAI_API_KEY=your-openai-api-key-here

# File Upload Configuration
UPLOAD_FOLDER=./uploads
MAX_CONTENT_LENGTH=16777216  # 16MB max file size
ALLOWED_EXTENSIONS=pdf,docx,doc,txt

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### **LLM Integration Setup**

For advanced legal insights, add your OpenAI API key:

1. Get an API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add it to your `.env` file:
   ```
   OPENAI_API_KEY=sk-your-actual-api-key-here
   ENABLE_LLM=true
   ```

## 🚀 **Running the Application**

1. **Start the Flask server**:
```bash
python app.py
```

2. **Open your browser** and navigate to `http://localhost:5000`

3. **Upload a contract file** and view comprehensive analysis results

## 📊 **Analysis Pipeline**

```
Document Upload → Text Extraction → Clause Extraction → Summarization → Risk Detection → LLM Analysis → Results Display
```

### **Step-by-Step Process**

1. **File Upload**: User uploads contract via web interface
2. **Text Extraction**: Converts document to analyzable text
3. **Clause Segmentation**: Splits text into logical contract sections
4. **Clause Classification**: Identifies clause types using AI
5. **Summarization**: Creates concise summaries of clauses and overall document
6. **Risk Detection**: Scans for potential legal and business risks
7. **LLM Analysis**: Advanced legal insights and recommendations
8. **Results Display**: Comprehensive analysis report with interactive UI

## 🔍 **Analysis Features**

### **Clause Types Detected**
- Termination, Confidentiality, Liability
- Payment, Governing Law, Dispute Resolution
- Force Majeure, Assignment, Amendments
- Notices, Severability, Entire Agreement
- Waiver, Survival, Indemnification

### **Risk Categories**
- **High Risk**: Automatic renewal, unlimited liability
- **Medium Risk**: Penalty fees, data ownership issues
- **Low Risk**: Mandatory arbitration, jurisdiction concerns

### **LLM-Powered Insights**
- **Legal Analysis**: Plain-language contract interpretation
- **Business Impact**: How clauses affect operations
- **Negotiation Points**: Key areas to negotiate
- **Compliance Assessment**: Regulatory and industry compliance
- **Risk Explanations**: Detailed risk analysis with mitigation strategies

## 📁 **Project Structure**

```
LegalScope/
├── app.py                    # Main Flask application
├── requirements.txt          # Python dependencies
├── README.md                # Project documentation
├── env_example.txt          # Environment variables template
├── .gitignore               # Git ignore file
├── test_app.py              # Test suite
├── test_pdf_extraction.py   # PDF extraction tests
├── test_llm_integration.py  # LLM integration tests
├── static/                  # Static files
│   ├── css/
│   │   └── style.css        # Custom styles
│   └── js/
│       └── main.js          # JavaScript functionality
├── templates/               # HTML templates
│   ├── base.html            # Base template
│   ├── index.html           # Main upload page
│   ├── results.html         # Analysis results
│   ├── about.html           # About page
│   ├── 404.html             # Error page
│   └── 500.html             # Server error page
├── utils/                   # Core analysis modules
│   ├── __init__.py
│   ├── text_extractor.py    # Document text extraction
│   ├── clause_extractor.py  # Clause identification & classification
│   ├── summarizer.py        # Text summarization
│   ├── risk_detector.py     # Risk detection
│   └── llm_analyzer.py      # LLM-powered legal analysis
├── data/                    # Sample data
│   └── sample_contract.txt  # Sample contract for testing
├── uploads/                 # Uploaded files (auto-created)
├── logs/                    # Application logs (auto-created)
└── models/                  # AI model cache (auto-created)
```

## 🔌 **API Endpoints**

### **Web Interface**
- `GET /` - Main upload page
- `POST /upload` - Upload and analyze contract
- `GET /about` - About page

### **REST API**
- `POST /api/analyze` - JSON API for contract analysis

### **Example API Usage**

```bash
curl -X POST -F "file=@contract.pdf" http://localhost:5000/api/analyze
```

**Response Example**:
```json
{
  "filename": "contract.pdf",
  "overall_summary": "This is a service agreement between...",
  "clauses": [
    {
      "type": "Termination",
      "text": "This agreement may be terminated...",
      "summary": "Either party can end the agreement with notice",
      "confidence": 0.85
    }
  ],
  "risks": [
    {
      "category": "auto_renewal",
      "text": "This agreement automatically renews...",
      "severity": "high",
      "confidence": 0.8
    }
  ],
  "llm_analysis": {
    "legal_insights": "This contract contains several standard terms...",
    "recommendations": [
      "Negotiate the automatic renewal clause",
      "Add liability caps to protect your business"
    ],
    "compliance_check": {
      "assessment": "Generally compliant with standard practices",
      "compliance_score": 0.75
    }
  },
  "total_clauses": 15,
  "risk_count": 3
}
```

## 🧪 **Testing**

### **Run Test Suite**
```bash
python test_app.py
```

### **Test PDF Extraction**
```bash
python test_pdf_extraction.py
```

### **Test LLM Integration**
```bash
python test_llm_integration.py
```

## 📈 **Performance**

Based on current testing:
- **Text Extraction**: 3946 characters from 4-page PDF
- **Clause Detection**: 11 clauses identified
- **Risk Detection**: 3 risks found
- **Processing Time**: ~2-3 minutes for complete analysis
- **LLM Analysis**: Additional 30-60 seconds for advanced insights

## 🔧 **Troubleshooting**

### **Common Issues**

1. **PDF Extraction Fails**
   - Ensure pdfplumber is installed: `pip install pdfplumber`
   - Check if PDF is password-protected or corrupted

2. **LLM Analysis Not Working**
   - Verify OpenAI API key is set in `.env`
   - Check `ENABLE_LLM=true` in environment variables
   - Ensure internet connection for API calls

3. **Models Not Loading**
   - First run may take time to download AI models
   - Check available disk space for model cache
   - Verify transformers and torch are installed

### **Logs**
Check application logs in `./logs/app.log` for detailed error information.

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 **Acknowledgments**

- Hugging Face for NLP models and transformers library
- OpenAI for GPT-4 API access
- Flask community for the web framework
- Bootstrap team for the UI framework

---

**Legal Disclaimer**: This tool provides AI-powered analysis for educational and business purposes. It is not a substitute for professional legal advice. Always consult with qualified legal counsel for important legal matters. 