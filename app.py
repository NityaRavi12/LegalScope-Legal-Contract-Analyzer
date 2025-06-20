import os
import logging
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from dotenv import load_dotenv

from utils.text_extractor import TextExtractor
from utils.clause_extractor import ClauseExtractor
from utils.summarizer import Summarizer
from utils.risk_detector import RiskDetector
from utils.llm_analyzer import LLMAnalyzer, LLMConfig

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.getenv('LOG_FILE', 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', './uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))  # 16MB
app.config['ALLOWED_EXTENSIONS'] = os.getenv('ALLOWED_EXTENSIONS', 'pdf,docx,doc,txt').split(',')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize components
text_extractor = TextExtractor()
clause_extractor = ClauseExtractor()
summarizer = Summarizer()
risk_detector = RiskDetector()

# Initialize LLM analyzer (optional)
llm_config = LLMConfig(
    enable_llm=os.getenv('ENABLE_LLM', 'false').lower() == 'true',
    provider=os.getenv('LLM_PROVIDER', 'openai'),
    model=os.getenv('LLM_MODEL', 'gpt-4')
)
llm_analyzer = LLMAnalyzer(llm_config)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    """Main page with upload form"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and analysis"""
    try:
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename or 'unknown_file')
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            logger.info(f"File uploaded: {filename}")
            
            # Process the file
            analysis_result = analyze_contract(filepath)
            
            return render_template('results.html', 
                                 filename=filename, 
                                 analysis=analysis_result)
        else:
            flash('File type not allowed. Please upload PDF, DOCX, DOC, or TXT files.', 'error')
            return redirect(request.url)
            
    except RequestEntityTooLarge:
        flash('File too large. Maximum size is 16MB.', 'error')
        return redirect(request.url)
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        flash('An error occurred while processing the file.', 'error')
        return redirect(request.url)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for contract analysis"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename or 'unknown_file')
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the file
            analysis_result = analyze_contract(filepath)
            
            return jsonify(analysis_result)
        else:
            return jsonify({'error': 'File type not allowed'}), 400
            
    except Exception as e:
        logger.error(f"API Error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def analyze_contract(filepath):
    """Main analysis pipeline"""
    try:
        # Step 1: Extract text from document
        logger.info("Extracting text from document...")
        try:
            text = text_extractor.extract_text(filepath)
            logger.info(f"Text extraction completed. Text length: {len(text) if text else 0}")
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise ValueError(f"Failed to extract text from document: {str(e)}")
        
        if not text or len(text.strip()) < 100:
            logger.warning(f"Extracted text is too short or empty: {len(text) if text else 0} characters")
            raise ValueError("Document appears to be empty or too short")
        
        # Step 2: Extract clauses
        logger.info("Extracting clauses...")
        clauses = clause_extractor.extract_clauses(text)
        logger.info(f"Clause extraction completed. Found {len(clauses)} clauses")
        
        # Step 3: Summarize clauses
        logger.info("Summarizing clauses...")
        summarized_clauses = []
        for clause in clauses:
            summary = summarizer.summarize(clause['text'])
            summarized_clauses.append({
                'type': clause['type'],
                'text': clause['text'],
                'summary': summary,
                'confidence': clause.get('confidence', 0.0)
            })
        
        # Step 4: Detect risks
        logger.info("Detecting risks...")
        risks = risk_detector.detect_risks(text, summarized_clauses)
        logger.info(f"Risk detection completed. Found {len(risks)} risks")
        
        # Step 5: Generate overall summary
        overall_summary = summarizer.summarize(text[:2000])  # First 2000 chars for overall summary
        
        # Step 6: LLM Analysis (if enabled)
        llm_analysis = {}
        if llm_analyzer.config.enable_llm:
            logger.info("Performing LLM analysis...")
            try:
                llm_analysis = llm_analyzer.analyze_contract_comprehensive(text, summarized_clauses, risks)
            except Exception as e:
                logger.warning(f"LLM analysis failed: {e}")
                llm_analysis = {}
        
        return {
            'filename': os.path.basename(filepath),
            'overall_summary': overall_summary,
            'clauses': summarized_clauses,
            'risks': risks,
            'total_clauses': len(summarized_clauses),
            'risk_count': len(risks),
            'llm_analysis': llm_analysis
        }
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        raise

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 