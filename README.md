# LexiSummarize: NLP-Based Extractive Text Summarizer

LexiSummarize is a professional, high-fidelity Python web application that leverages Natural Language Processing (NLP) to perform extractive text summarization on long documents. The system decomposes input documents into sentences, ranks their informational density using multiple mathematical/linguistic algorithms, and compiles them into a condensed, high-value summary.

## 🚀 Live Demo & Deployment
This application is designed to run seamlessly both locally and when deployed to **Streamlit Cloud**.
- The application dynamically manages environment setup at runtime, automatically downloading missing spaCy linguistic assets (`en_core_web_sm`) and NLTK sentence tokenization databases (`punkt`).

---

## 🛠️ Architecture & Tech Stack

### Technology Stack
- **Core Engine**: Python 3.9+
- **Frontend Dashboard**: Streamlit (with custom CSS style injection)
- **Linguistic Processing**: spaCy (`en_core_web_sm` pipeline) & NLTK (Tokenization)
- **Mathematical Vectorization**: Scikit-Learn (`TfidfVectorizer`, Cosine Similarity matrices)
- **Graph Computations**: NetworkX (PageRank implementation for TextRank)
- **Semantic Model**: Sumy (Latent Semantic Analysis via Singular Value Decomposition)
- **File Ingestion**: pdfplumber (PDF extraction), python-docx (DOCX parsing)
- **Document Exporting**: fpdf2 (Executive PDF templates), python-docx (Word documents)
- **Visual Analytics**: Matplotlib & Seaborn (styled themes)

### Folder Structure
```
TextSummarizer/
│
├── app.py              # Main Streamlit Dashboard (Routing, tabs, sidebar control, styling)
├── preprocessing.py    # Document text ingestion, tokenization, lemmatization, POS tags
├── summarizer.py       # Core algorithms (TextRank, TF-IDF, Frequency-Based, LSA)
├── visualization.py    # Matplotlib graphs (Sentence importance, word frequency, comparison)
├── export.py           # Report generators (TXT, DOCX, custom FPDF2)
├── utils.py            # System helpers (NLTK/spaCy setup, assets, directory cleaners)
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

---

## 🧠 Extractive Summarization Algorithms

Extractive summarization selects the most representative sentences directly from the source text. LexiSummarize offers four state-of-the-art extractive techniques:

1. **TextRank (Graph-Based)**:
   - A graph-based ranking algorithm based on Google's PageRank.
   - Sentences are treated as nodes in a graph. Edges represent the cosine similarity between the TF-IDF vector representations of the sentences.
   - PageRank runs iteratively to determine sentence centrality. Sentences that share vocabulary with many other central sentences are prioritized.

2. **TF-IDF (Statistical-Weighted)**:
   - Evaluates sentences based on Term Frequency-Inverse Document Frequency.
   - Fits a TF-IDF vectorizer across the individual sentences of the document.
   - Scores sentences by summing the TF-IDF weights of their constituent words. This emphasizes sentences containing terms that are unique and descriptive of the document's core subject.

3. **Frequency-Based (Linguistic Heuristic)**:
   - Measures term frequencies within the document (excluding common stopwords and punctuation).
   - Word frequencies are normalized by the maximum term frequency in the vocabulary.
   - Scores sentences by summing the normalized frequency weights of their active words, then normalizes by the sentence length to avoid bias towards longer sentences.

4. **Latent Semantic Analysis (LSA - Semantic SVD)**:
   - Performs a Singular Value Decomposition (SVD) on the term-document matrix representing the sentences.
   - Groups terms and sentences into latent "concepts" or "topics."
   - Ranks sentences by their representation across the primary latent dimensions, selecting sentences that capture the broadest semantic variance in the document.

---

## 💻 Local Installation & Setup

Follow these steps to run the application on your local machine:

1. **Clone the project repository** (or copy the workspace folder):
   ```bash
   cd TextSummarizer
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

5. Open your browser to `http://localhost:8501` to view the dashboard.

---

## ☁️ Deployment to Streamlit Cloud

To deploy this application to **Streamlit Community Cloud**:
1. Push the code repository to a GitHub account.
2. Log in to [Streamlit Share](https://share.streamlit.io/).
3. Click **New App**, select your repository, branch, and set the entry file to `app.py`.
4. Click **Deploy**. The application's `utils.py` will handle downloads of all missing assets dynamically upon container spin-up.

---

## 🔒 Robust Error Handling & Performance

- **File Encoding Protection**: Ingests TXT documents using multiple fallback encodings (UTF-8, Latin-1, CP-1252) to avoid standard decoding exceptions.
- **PDF Compatibility Mapping**: Filters out smart quotes, em-dashes, and unsupported Unicode symbols during PDF generation to prevent FPDF layout errors.
- **Automatic Convergers**: PageRank similarity graph calculations are wrapped in fallbacks (degree centrality) if graph iterations fail to converge on large or repetitive texts.
- **Auto-Cleanup Daemon**: Periodically wipes files in `uploads/` and `outputs/` older than 1 hour to prevent server storage bloat on shared cloud instances.
