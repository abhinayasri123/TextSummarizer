import os
import shutil
import time
import spacy
import streamlit as st
import nltk

def initialize_directories():
    """Create necessary directories for uploads, outputs, and assets, and download NLTK requirements."""
    dirs = ['uploads', 'outputs', 'assets']
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    # Download NLTK requirements
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('punkt_tab', quiet=True)
    except Exception as e:
        print(f"Failed to download NLTK data: {e}")


def clear_temp_directories():
    """Clear uploaded and exported temporary files older than 1 hour."""
    now = time.time()
    for folder in ['uploads', 'outputs']:
        if not os.path.exists(folder):
            continue
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            # If file is older than 1 hour (3600 seconds), delete it
            try:
                if os.path.isfile(filepath) or os.path.islink(filepath):
                    if os.stat(filepath).st_mtime < now - 3600:
                        os.unlink(filepath)
                elif os.path.isdir(filepath):
                    if os.stat(filepath).st_mtime < now - 3600:
                        shutil.rmtree(filepath)
            except Exception as e:
                print(f"Error deleting temp file {filepath}: {e}")

def load_spacy_model():
    """Load spaCy's en_core_web_sm model, downloading it if not present."""
    model_name = "en_core_web_sm"
    try:
        nlp = spacy.load(model_name)
        return nlp
    except OSError:
        # Model not found, let's download it
        with st.spinner("Downloading spaCy NLP English model (en_core_web_sm)... This may take a moment."):
            try:
                spacy.cli.download(model_name)
                nlp = spacy.load(model_name)
                return nlp
            except Exception as e:
                st.error(f"Failed to download spaCy model automatically: {e}")
                # Fallback list or raise error
                raise e

def inject_custom_css():
    """Inject custom modern styling into Streamlit for a premium look."""
    st.markdown("""
        <style>
        /* Modern font adjustments */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
        }

        /* Styling cards and containers */
        .metric-card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(5px);
            -webkit-backdrop-filter: blur(5px);
            margin-bottom: 1rem;
        }

        .highlighted-text {
            line-height: 1.8;
            font-size: 1.05rem;
            padding: 10px;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.02);
            border-left: 4px solid #6366f1;
        }

        /* Custom buttons styling */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
            color: white !important;
            border: none !important;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.5);
            color: white !important;
        }

        /* Tabs custom styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }

        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px;
            color: #64748b;
            font-size: 16px;
            font-weight: 600;
        }

        .stTabs [aria-selected="true"] {
            color: #6366f1 !important;
            border-bottom: 2px solid #6366f1 !important;
        }

        /* Success & Info alert customized */
        div[data-testid="stNotification"] {
            border-radius: 8px;
            border-left: 5px solid #10b981;
        }
        </style>
    """, unsafe_allow_html=True)
