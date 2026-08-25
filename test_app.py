import os
import sys

# Add current folder to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("1. Testing library imports...")
    import streamlit as st
    import spacy
    import nltk
    import sklearn
    import sumy
    import pandas as pd
    import matplotlib
    import pdfplumber
    import docx
    import fpdf
    import networkx as nx
    print("-> All libraries imported successfully.")

    print("\n2. Testing utils.py (directory setup and model download)...")
    from utils import initialize_directories, load_spacy_model
    initialize_directories()
    nlp = load_spacy_model()
    print("-> spaCy model loaded successfully.")

    print("\n3. Testing preprocessing.py (text parsing)...")
    from preprocessing import clean_text, run_nlp_pipeline
    test_text = "This is the first sentence. This is the second sentence about artificial intelligence. Natural language processing is fun and exciting."
    cleaned = clean_text(test_text)
    doc, sentences, tokens_df, stats = run_nlp_pipeline(cleaned, nlp)
    print(f"-> Parsed text: {len(sentences)} sentences, {stats['word_count']} words.")
    print(f"Tokens dataframe preview:\n{tokens_df.head(2)}")

    print("\n4. Testing summarizer.py...")
    from summarizer import (
        summarize_frequency, 
        summarize_tfidf, 
        summarize_textrank, 
        summarize_lsa,
        highlight_keywords
    )
    
    # Frequency
    sum_freq, scores_freq, kw_freq = summarize_frequency(sentences, nlp, 2)
    print(f"-> Frequency Summary: '{sum_freq}' (Keywords: {kw_freq[:3]})")
    
    # TF-IDF
    sum_tfidf, scores_tfidf, kw_tfidf = summarize_tfidf(sentences, 2)
    print(f"-> TF-IDF Summary: '{sum_tfidf}' (Keywords: {kw_tfidf[:3]})")
    
    # TextRank
    sum_tr, scores_tr, kw_tr = summarize_textrank(sentences, 2)
    print(f"-> TextRank Summary: '{sum_tr}'")
    
    # LSA
    sum_lsa, scores_lsa, kw_lsa = summarize_lsa(sentences, 2)
    print(f"-> LSA Summary: '{sum_lsa}'")
    
    # Highlight
    highlighted = highlight_keywords(test_text, kw_freq)
    print(f"-> Highlighted snippet check: {highlighted[:100]}...")

    print("\n5. Testing export.py...")
    from export import export_to_txt, export_to_docx, export_to_pdf
    meta = {
        "algorithm": "TextRank",
        "compression_ratio": "50%",
        "orig_words": stats['word_count'],
        "sum_words": 10,
        "orig_sents": len(sentences),
        "sum_sents": 2,
        "timestamp": "2026-07-28 12:00:00",
        "keywords": kw_tr
    }
    
    txt_f = export_to_txt(sum_tr, meta, "outputs/test_summary.txt")
    print(f"-> TXT export written to {txt_f}")
    
    docx_f = export_to_docx(sum_tr, meta, "outputs/test_summary.docx")
    print(f"-> DOCX export written to {docx_f}")
    
    pdf_f = export_to_pdf(sum_tr, meta, "outputs/test_summary.pdf")
    print(f"-> PDF export written to {pdf_f}")

    print("\n6. Testing visualization.py...")
    from visualization import plot_word_frequency, plot_sentence_importance, plot_summary_stats_comparison
    fig_freq = plot_word_frequency(tokens_df)
    fig_imp = plot_sentence_importance(scores_tr, [0, 2])
    fig_comp = plot_summary_stats_comparison(stats['word_count'], 10)
    print("-> Matplotlib figures generated successfully.")
    
    print("\n=== ALL TESTS COMPLETED SUCCESSFULLY! The system is fully operational. ===")
    
except Exception as e:
    print(f"\n!!! TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
