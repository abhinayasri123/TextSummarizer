import os
import re
import pdfplumber
import docx
import pandas as pd
import spacy

def extract_text_from_file(filepath, file_extension):
    """
    Extracts text from TXT, PDF, or DOCX files.
    """
    text = ""
    file_extension = file_extension.lower().strip('.')
    
    if file_extension == 'txt':
        encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-16']
        for encoding in encodings:
            try:
                with open(filepath, 'r', encoding=encoding) as f:
                    text = f.read()
                break
            except UnicodeDecodeError:
                continue
        if not text:
            raise ValueError("Could not decode plain text file. Please check file encoding.")

    elif file_extension == 'pdf':
        try:
            with pdfplumber.open(filepath) as pdf:
                pages_text = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append(page_text)
                text = "\n".join(pages_text)
        except Exception as e:
            raise RuntimeError(f"Error reading PDF: {e}")

    elif file_extension in ['docx', 'doc']:
        try:
            doc = docx.Document(filepath)
            paragraphs = [p.text for p in doc.paragraphs]
            text = "\n".join(paragraphs)
        except Exception as e:
            raise RuntimeError(f"Error reading DOCX: {e}")
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")
        
    return text

def clean_text(text):
    """
    Performs basic text cleanup (merging whitespace, formatting fixes).
    """
    if not text:
        return ""
    # Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Standardize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Replace more than 3 consecutive newlines with exactly 2 newlines (paragraph split)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def run_nlp_pipeline(text, nlp):
    """
    Runs the spaCy pipeline on cleaned text.
    Returns:
      - doc: The spaCy Doc object
      - sentences: List of raw strings for each sentence
      - tokens_df: A Pandas DataFrame detailing token attributes (Token, Lemma, POS, Stopword)
      - stats: A dictionary with stats (word count, sentence count, char count, avg sentence length)
    """
    doc = nlp(text)
    
    # Sentence splitting
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 0]
    
    # Build token list for analysis
    token_records = []
    word_count = 0
    non_stopword_words = []
    
    for token in doc:
        # We track word count based on alphabetical/numeric tokens (ignoring punctuation)
        if not token.is_punct and not token.is_space:
            word_count += 1
            if not token.is_stop:
                non_stopword_words.append(token.lemma_.lower())
                
        token_records.append({
            "Token": token.text,
            "Lemma": token.lemma_,
            "POS": token.pos_,
            "POS_Description": spacy.explain(token.pos_) if token.pos_ else "",
            "Is_Stopword": token.is_stop,
            "Is_Punctuation": token.is_punct,
            "Is_Alpha": token.is_alpha
        })
        
    tokens_df = pd.DataFrame(token_records)
    
    # Calculate stats
    stats = {
        "word_count": word_count,
        "sentence_count": len(sentences),
        "char_count": len(text),
        "avg_sentence_length": round(word_count / len(sentences), 2) if len(sentences) > 0 else 0,
        "estimated_reading_time_min": round(word_count / 200, 2)  # 200 WPM average reading speed
    }
    
    return doc, sentences, tokens_df, stats
