import os
import time
from datetime import datetime
import streamlit as st
import pandas as pd

# Project modules
from utils import (
    initialize_directories, 
    clear_temp_directories, 
    load_spacy_model, 
    inject_custom_css
)
from preprocessing import extract_text_from_file, clean_text, run_nlp_pipeline
from summarizer import (
    summarize_frequency, 
    summarize_tfidf, 
    summarize_textrank, 
    summarize_lsa, 
    highlight_keywords
)
from visualization import (
    plot_word_frequency, 
    plot_sentence_importance, 
    plot_summary_stats_comparison
)
from export import export_to_pdf, export_to_docx, export_to_txt

# Page configuration
st.set_page_config(
    page_title="LexiSummarize | Professional NLP Text Summarizer",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize paths and variables
initialize_directories()
clear_temp_directories()

# Load the spaCy model
try:
    nlp = load_spacy_model()
except Exception as e:
    st.error(f"Critical error loading spaCy NLP Model: {e}")
    st.stop()

# Load Custom Theme Styles
inject_custom_css()

# Sample text for quick testing
SAMPLE_TEXT = """Artificial Intelligence (AI) and Machine Learning (ML) are transforming industries globally. At its core, Artificial Intelligence refers to the simulation of human intelligence in machines that are programmed to think and learn like humans. These systems can perform complex tasks such as visual perception, speech recognition, decision-making, and translation between languages. Machine Learning, a subset of AI, focuses on the development of algorithms that allow computers to learn from and make predictions or decisions based on data. Rather than being explicitly programmed to perform a task, the computer uses input data and statistical models to improve its performance automatically over time.

Deep Learning is a further specialized subfield of Machine Learning based on artificial neural networks. These networks are inspired by the structure and function of the human brain, specifically the biological neural networks. Deep learning algorithms have been highly successful in computer vision, natural language processing, and audio recognition. Through deep neural layers, computers can identify patterns, extract features, and build representations of high-dimensional data without manual feature engineering.

However, the rapid expansion of AI also raises significant ethical and social concerns. Issues such as algorithmic bias, data privacy, and automation-induced job displacement are topics of active debate. Algorithmic bias occurs when AI systems produce systematically prejudiced results based on biased training data. For instance, facial recognition algorithms have shown higher error rates for minority groups. Data privacy is another critical concern, as modern AI models require vast repositories of user data to train effectively, sometimes compromising individual anonymity.

Furthermore, explainable AI (XAI) has emerged as a crucial area of research. As models become more complex, understanding how they arrive at specific conclusions is difficult, creating a "black box" problem. Stakeholders need to trust automated decisions, especially in critical sectors like healthcare, criminal justice, and autonomous vehicles. Engineers are developing techniques to make complex neural decisions interpretable for humans, balancing accuracy with transparency. In conclusion, while AI offers unprecedented opportunities for efficiency and innovation, establishing robust ethical frameworks and governance guidelines is essential for responsible development."""

# App Title & Header
st.markdown("""
    <div style="background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%); padding: 2rem; border-radius: 16px; margin-bottom: 2rem; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 10px 30px rgba(0,0,0,0.3)">
        <h1 style="color: white; margin: 0; font-size: 2.8rem; font-weight: 700; background: linear-gradient(90deg, #6366f1, #a855f7, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            LexiSummarize NLP Dashboard
        </h1>
        <p style="color: #cbd5e1; font-size: 1.1rem; margin: 0.5rem 0 0 0; font-weight: 300;">
            Professional Extractive Document Summarization powered by advanced Natural Language Processing
        </p>
    </div>
""", unsafe_allow_html=True)

# Main layout split into Sidebar and Main Content
with st.sidebar:
    st.markdown("### 📥 Input Configuration")
    
    # Input source toggle
    input_source = st.radio(
        "Choose Input Method:",
        ["Paste Manually", "Upload Document"],
        index=0
    )
    
    raw_text = ""
    
    if input_source == "Paste Manually":
        raw_text = st.text_area(
            "Paste your document text here:",
            height=250,
            placeholder="Type or paste long document text here..."
        )
        
        # Load sample text helper button
        if st.button("Load Sample Science Article"):
            raw_text = SAMPLE_TEXT
            # Rerun or update text area state by forcing a slider/state reset
            st.session_state["manual_text"] = SAMPLE_TEXT
            st.rerun()
            
        # Handle session state persistence for sample load
        if "manual_text" in st.session_state and not raw_text:
            raw_text = st.session_state["manual_text"]
            
    else:
        uploaded_file = st.file_uploader(
            "Upload TXT, PDF, or DOCX:",
            type=["txt", "pdf", "docx"]
        )
        if uploaded_file is not None:
            # Save temporary file
            temp_path = os.path.join("uploads", uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Extract text
            file_ext = os.path.splitext(uploaded_file.name)[1]
            with st.spinner("Extracting text from uploaded file..."):
                try:
                    raw_text = extract_text_from_file(temp_path, file_ext)
                except Exception as e:
                    st.error(f"Error parsing document: {e}")
                    raw_text = ""
        else:
            st.info("Upload a document file to proceed.")
            raw_text = ""

    st.markdown("---")
    st.markdown("### ⚙️ Summarization Controls")
    
    # Algorithm selection
    algorithm = st.selectbox(
        "Summarization Algorithm:",
        ["TextRank (Graph-Based)", "TF-IDF (Statistical)", "Frequency-Based (Heuristic)", "LSA (Semantic)"]
    )
    
    # Sentence slider configurations
    slider_mode = st.radio(
        "Select Summary Length By:",
        ["Sentence Count", "Percentage of Original"],
        horizontal=True
    )
    
    # Highlight configuration
    st.markdown("---")
    st.markdown("### 🎨 Keywords & Highlight Options")
    highlight_enabled = st.checkbox("Highlight Extract Keywords", value=True)
    highlight_color = st.color_picker("Highlight Background Color", value="#fde047")

# Verify we have text
cleaned_text = clean_text(raw_text)

if not cleaned_text:
    st.markdown("""
        <div style="background-color: rgba(99, 102, 241, 0.05); border-left: 5px solid #6366f1; padding: 2rem; border-radius: 8px; text-align: center; margin-top: 2rem;">
            <h3 style="color: #6366f1; margin-top: 0;">Welcome to LexiSummarize!</h3>
            <p style="color: #475569; max-width: 600px; margin: 0 auto 1.5rem auto;">
                To generate a summary, please upload a TXT, PDF, or DOCX document using the sidebar uploader or click the button below to load a sample scientific article.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Main content sample button
    if st.button("Load Demo Article", key="demo_btn"):
        st.session_state["manual_text"] = SAMPLE_TEXT
        st.rerun()
        
    st.stop()

# Run spaCy preprocessing on the text
with st.spinner("Analyzing text layout and parts of speech..."):
    doc, sentences, tokens_df, nlp_stats = run_nlp_pipeline(cleaned_text, nlp)

total_sentences = nlp_stats["sentence_count"]

if total_sentences == 0:
    st.warning("The input text does not contain any valid sentences. Please check your document.")
    st.stop()

# Calculate Summary Target Count based on slider mode
with st.sidebar:
    if slider_mode == "Sentence Count":
        # Dynamic ceiling for sentences
        target_sentences = st.slider(
            "Number of Sentences:",
            min_value=1,
            max_value=max(1, total_sentences),
            value=min(3, total_sentences)
        )
    else:
        percentage = st.slider(
            "Percentage of Document:",
            min_value=10,
            max_value=90,
            value=30,
            step=5
        )
        target_sentences = max(1, round((percentage / 100.0) * total_sentences))
        st.caption(f"Equivalent to **{target_sentences}** of {total_sentences} sentences.")

# Run Summarizer & Measure Processing Time
start_time = time.time()

with st.spinner(f"Running {algorithm} Summarizer..."):
    summary_text = ""
    scores = {}
    keywords = []
    
    if "TextRank" in algorithm:
        summary_text, scores, keywords = summarize_textrank(sentences, target_sentences)
    elif "TF-IDF" in algorithm:
        summary_text, scores, keywords = summarize_tfidf(sentences, target_sentences)
    elif "Frequency-Based" in algorithm:
        summary_text, scores, keywords = summarize_frequency(sentences, nlp, target_sentences)
    elif "LSA" in algorithm:
        summary_text, scores, keywords = summarize_lsa(sentences, target_sentences)

processing_time_ms = round((time.time() - start_time) * 1000, 2)

# Summarization stats calculations
orig_word_cnt = nlp_stats["word_count"]
sum_word_cnt = len([tok for tok in nlp(summary_text) if not tok.is_punct and not tok.is_space])
compression_ratio = round((1 - (sum_word_cnt / max(1, orig_word_cnt))) * 100, 1)

# Tab Layout
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Summarizer Dashboard", 
    "🔍 NLP Token Analyzer", 
    "📈 Analytics & Visuals", 
    "💾 Export Center"
])

# ==================== TAB 1: DASHBOARD ====================
with tab1:
    # Metric KPI Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.9rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Original Words</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1e293b; margin-top: 0.2rem;">{orig_word_cnt}</div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.1rem;">{total_sentences} Sentences</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.9rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Summary Words</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #6366f1; margin-top: 0.2rem;">{sum_word_cnt}</div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.1rem;">{target_sentences} Sentences</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.9rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Compression Ratio</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #10b981; margin-top: 0.2rem;">{compression_ratio}%</div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.1rem;">Size reduction rate</div>
            </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 0.9rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Processing Time</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #a855f7; margin-top: 0.2rem;">{processing_time_ms} ms</div>
                <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.1rem;">NLP & Engine latency</div>
            </div>
        """, unsafe_allow_html=True)

    # Main text layout panels
    col_orig, col_sum = st.columns(2)
    
    with col_orig:
        st.subheader("📄 Original Text Document")
        if highlight_enabled:
            highlighted_orig = highlight_keywords(cleaned_text, keywords, highlight_color)
            st.markdown(f'<div class="highlighted-text" style="max-height: 500px; overflow-y: auto;">{highlighted_orig}</div>', unsafe_allow_html=True)
        else:
            st.text_area("Original text content:", value=cleaned_text, height=500, disabled=True)
            
    with col_sum:
        st.subheader("✨ Summarized Output")
        if highlight_enabled:
            highlighted_sum = highlight_keywords(summary_text, keywords, highlight_color)
            st.markdown(f'<div class="highlighted-text" style="max-height: 500px; overflow-y: auto; border-left-color: #10b981;">{highlighted_sum}</div>', unsafe_allow_html=True)
        else:
            st.text_area("Summarized content output:", value=summary_text, height=500, disabled=True)
            
    # Add key extracted terms tags at the bottom of the dashboard
    if keywords:
        st.markdown("### 🔑 Key Concepts Extracted")
        tag_html = " ".join([
            f'<span style="background: rgba(99, 102, 241, 0.1); color: #4f46e5; font-size: 0.9rem; padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: 600; margin-right: 0.5rem; margin-bottom: 0.5rem; display: inline-block; border: 1px solid rgba(99, 102, 241, 0.2);">{kw}</span>'
            for kw in keywords
        ])
        st.markdown(tag_html, unsafe_allow_html=True)

# ==================== TAB 2: NLP TOKENS ====================
with tab2:
    st.markdown("### 🔍 Linguistic Component Decomposition")
    st.markdown("Inspect every token in the document, along with its Lemmatized (base) form and grammatical Part-of-Speech tag.")
    
    # Filter controls for the token grid
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        pos_filter = st.multiselect(
            "Filter by POS Grammatical Categories:",
            options=sorted(tokens_df['POS'].unique()),
            default=[]
        )
    with col_f2:
        stop_filter = st.selectbox(
            "Filter Stopwords:",
            ["Show All", "Exclude Stopwords Only", "Show Stopwords Only"]
        )
        
    filtered_tokens_df = tokens_df.copy()
    if pos_filter:
        filtered_tokens_df = filtered_tokens_df[filtered_tokens_df['POS'].isin(pos_filter)]
    if stop_filter == "Exclude Stopwords Only":
        filtered_tokens_df = filtered_tokens_df[filtered_tokens_df['Is_Stopword'] == False]
    elif stop_filter == "Show Stopwords Only":
        filtered_tokens_df = filtered_tokens_df[filtered_tokens_df['Is_Stopword'] == True]

    # Show basic counts
    st.write(f"Displaying **{len(filtered_tokens_df)}** of **{len(tokens_df)}** tokens in document.")
    
    # Render dataframe
    st.dataframe(
        filtered_tokens_df[["Token", "Lemma", "POS", "POS_Description", "Is_Stopword", "Is_Punctuation", "Is_Alpha"]],
        use_container_width=True,
        height=400
    )
    
    # Grammar breakdown charts
    st.markdown("### 📊 Grammar & Composition Analytics")
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # Stopwords Ratio
        stopword_counts = tokens_df['Is_Stopword'].value_counts()
        stop_ratio = round((stopword_counts.get(True, 0) / len(tokens_df)) * 100, 1) if len(tokens_df) > 0 else 0
        
        st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div style="font-size: 1rem; color: #64748b; font-weight: 600;">Stopword Composition</div>
                <div style="font-size: 3rem; font-weight: 700; color: #f59e0b; margin: 0.5rem 0;">{stop_ratio}%</div>
                <p style="color: #64748b; font-size: 0.9rem;">
                    {stopword_counts.get(True, 0)} of {len(tokens_df)} tokens are common grammatical connectives/stopwords.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
    with col_g2:
        # Top Parts of Speech (excl. space, punctuation)
        clean_pos_df = tokens_df[~tokens_df['Is_Punctuation'] & (tokens_df['POS'] != 'SPACE')]
        pos_counts = clean_pos_df['POS_Description'].value_counts().head(5)
        if not pos_counts.empty:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("<div style='font-size: 1rem; color: #64748b; font-weight: 600; margin-bottom: 0.8rem;'>Top POS Classes</div>", unsafe_allow_html=True)
            for pos_name, count in pos_counts.items():
                pct = round((count / len(clean_pos_df)) * 100, 1)
                st.markdown(f"**{pos_name}**: {count} tokens ({pct}%)")
            st.markdown("</div>", unsafe_allow_html=True)

# ==================== TAB 3: VISUALIZATIONS ====================
with tab3:
    st.markdown("### 📈 Visual Text Analytics")
    
    # Layout with Word Frequency and Sentence Importance
    col_vis1, col_vis2 = st.columns([1, 1])
    
    with col_vis1:
        st.markdown("#### Word Frequency Distribution")
        fig_freq = plot_word_frequency(tokens_df)
        st.pyplot(fig_freq)
        
    with col_vis2:
        st.markdown("#### Sentence Importance Over Time")
        
        # Calculate summary sentence indices
        summary_indices = []
        for i, sent in enumerate(sentences):
            if sent in summary_text:
                summary_indices.append(i)
                
        fig_imp = plot_sentence_importance(scores, summary_indices)
        st.pyplot(fig_imp)

    # Word count compression chart
    st.markdown("---")
    col_comp1, col_comp2 = st.columns([1, 1])
    with col_comp1:
        st.markdown("#### Text Reduction Impact Visualization")
        fig_comp = plot_summary_stats_comparison(orig_word_cnt, sum_word_cnt)
        st.pyplot(fig_comp)
    with col_comp2:
        # Extra details cards
        st.markdown("#### Meta Analysis Details")
        st.markdown(f"""
            - **Average Sentence Length**: {nlp_stats['avg_sentence_length']} words.
            - **Original Reading Time**: ~{nlp_stats['estimated_reading_time_min']} minutes.
            - **Summary Reading Time**: ~{round(sum_word_cnt / 200, 2)} minutes.
            - **Document Density**: {len(tokens_df)} tokens total, parsed across {nlp_stats['char_count']} characters.
        """)

# ==================== TAB 4: EXPORTS ====================
with tab4:
    st.markdown("### 💾 Export Generated Summaries")
    st.write("Save your summarized output in one of the professional document layouts below.")
    
    # Metadata for exporters
    export_meta = {
        "algorithm": algorithm,
        "compression_ratio": f"{compression_ratio}%",
        "orig_words": orig_word_cnt,
        "sum_words": sum_word_cnt,
        "orig_sents": total_sentences,
        "sum_sents": target_sentences,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "keywords": keywords
    }
    
    col_ex1, col_ex2, col_ex3 = st.columns(3)
    
    with col_ex1:
        st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); text-align: center;">
                <h4 style="margin: 0; color: #1e293b;">📄 Plain Text (.txt)</h4>
                <p style="color: #64748b; font-size: 0.85rem; margin: 0.5rem 0 1.2rem 0;">Clean, minimal, lightweight layout file.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Prepare file path
        txt_path = os.path.join("outputs", "summary_report.txt")
        export_to_txt(summary_text, export_meta, txt_path)
        
        with open(txt_path, "rb") as f:
            st.download_button(
                label="Download TXT Report",
                data=f,
                file_name="NLP_Summary_Report.txt",
                mime="text/plain",
                use_container_width=True
            )
            
    with col_ex2:
        st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); text-align: center;">
                <h4 style="margin: 0; color: #1e293b;">📘 Microsoft Word (.docx)</h4>
                <p style="color: #64748b; font-size: 0.85rem; margin: 0.5rem 0 1.2rem 0;">Sleek corporate styling and editable structure.</p>
            </div>
        """, unsafe_allow_html=True)
        
        docx_path = os.path.join("outputs", "summary_report.docx")
        export_to_docx(summary_text, export_meta, docx_path)
        
        with open(docx_path, "rb") as f:
            st.download_button(
                label="Download Word Report",
                data=f,
                file_name="NLP_Summary_Report.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )
            
    with col_ex3:
        st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.05); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); text-align: center;">
                <h4 style="margin: 0; color: #1e293b;">📕 Adobe PDF Document</h4>
                <p style="color: #64748b; font-size: 0.85rem; margin: 0.5rem 0 1.2rem 0;">Polished executive summary card and header styles.</p>
            </div>
        """, unsafe_allow_html=True)
        
        pdf_path = os.path.join("outputs", "summary_report.pdf")
        export_to_pdf(summary_text, export_meta, pdf_path)
        
        with open(pdf_path, "rb") as f:
            st.download_button(
                label="Download PDF Report",
                data=f,
                file_name="NLP_Summary_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
