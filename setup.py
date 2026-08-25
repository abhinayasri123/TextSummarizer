#!/usr/bin/env python3
"""
Setup script run by cloud platforms like Streamlit Community Cloud
to ensure all runtime dependencies (spaCy model, NLTK data) are downloaded.
This runs BEFORE app.py is started.
"""
import subprocess
import sys

def install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])

# Ensure seaborn is installed (sometimes missed on cloud)
try:
    import seaborn
except ImportError:
    print("Installing seaborn...")
    install("seaborn")

# Download spaCy English model
try:
    import spacy
    spacy.load("en_core_web_sm")
    print("spaCy model already available.")
except OSError:
    print("Downloading spaCy en_core_web_sm model...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])

# Download NLTK data
import nltk
print("Downloading NLTK punkt tokenizer...")
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

print("All runtime assets ready.")
