import numpy as np
import re
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

# Sumy imports
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

def summarize_frequency(sentences, nlp, num_sentences):
    """
    Summarizes text using word frequency.
    1. Computes frequency of each word (ignoring stop words and punctuation).
    2. Scores sentences by summing normalized word frequencies.
    3. Selects top scoring sentences, maintaining chronological order.
    """
    if not sentences:
        return "", {}, []

    # Join sentences to parse as a single doc for vocabulary statistics
    full_text = " ".join(sentences)
    doc = nlp(full_text)
    
    # Calculate word frequencies
    word_frequencies = {}
    for token in doc:
        word = token.lemma_.lower()
        if not token.is_stop and not token.is_punct and token.is_alpha:
            word_frequencies[word] = word_frequencies.get(word, 0) + 1
            
    if not word_frequencies:
        # Fallback to returning first sentences if no alpha words exist
        return " ".join(sentences[:num_sentences]), {i: 1.0 for i, _ in enumerate(sentences[:num_sentences])}, list(word_frequencies.keys())

    # Normalize frequencies
    max_freq = max(word_frequencies.values())
    for word in word_frequencies:
        word_frequencies[word] = word_frequencies[word] / max_freq
        
    # Score sentences
    sentence_scores = {}
    for i, sent in enumerate(sentences):
        sent_doc = nlp(sent)
        score = 0
        word_count = 0
        for token in sent_doc:
            word = token.lemma_.lower()
            if word in word_frequencies:
                score += word_frequencies[word]
                word_count += 1
        # Normalize by length to prevent favoring excessively long sentences
        sentence_scores[i] = score / max(1, word_count)

    # Sort and pick top sentences
    top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    top_indices.sort() # Maintain chronological order
    
    summary = " ".join([sentences[i] for i in top_indices])
    
    # Extract top keywords (highest frequency words)
    top_keywords = sorted(word_frequencies, key=word_frequencies.get, reverse=True)[:15]
    
    return summary, sentence_scores, top_keywords


def summarize_tfidf(sentences, num_sentences):
    """
    Summarizes text using Sentence TF-IDF.
    1. Computes TF-IDF vector for each sentence.
    2. Scores sentences by summing TF-IDF weights of their words.
    3. Selects top sentences and restores order.
    """
    if not sentences:
        return "", {}, []

    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(sentences)
    except ValueError:
        # Occurs if all sentences are stopwords
        return " ".join(sentences[:num_sentences]), {i: 1.0 for i, _ in enumerate(sentences[:num_sentences])}, []

    sentence_scores = {}
    feature_names = vectorizer.get_feature_names_out()
    
    # Sum TF-IDF scores for each sentence
    for i, sentence in enumerate(sentences):
        row = tfidf_matrix.getrow(i).toarray()[0]
        # Sum non-zero tfidf values for words in sentence
        score = np.sum(row)
        sentence_scores[i] = score

    top_indices = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    top_indices.sort()
    
    summary = " ".join([sentences[i] for i in top_indices])
    
    # Extract keywords based on sum of TF-IDF scores across sentences
    tfidf_sums = np.asarray(tfidf_matrix.sum(axis=0)).ravel()
    keyword_scores = [(feature_names[i], tfidf_sums[i]) for i in range(len(feature_names))]
    top_keywords = [word for word, score in sorted(keyword_scores, key=lambda x: x[1], reverse=True)[:15]]
    
    return summary, sentence_scores, top_keywords


def summarize_textrank(sentences, num_sentences):
    """
    Summarizes text using TextRank algorithm.
    1. Computes TF-IDF vectors for sentences.
    2. Builds similarity matrix using cosine similarity.
    3. Computes PageRank scores.
    4. Selects top sentences in original order.
    """
    if not sentences:
        return "", {}, []

    # If document has very few sentences, TextRank won't work well; return early
    if len(sentences) <= num_sentences:
        return " ".join(sentences), {i: 1.0 for i in range(len(sentences))}, []

    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(sentences)
    except ValueError:
        return " ".join(sentences[:num_sentences]), {i: 1.0 for i, _ in enumerate(sentences[:num_sentences])}, []

    # Compute sentence similarity matrix
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Build NetworkX graph
    nx_graph = nx.from_numpy_array(similarity_matrix)
    
    # Run PageRank (adjust tolerance if it doesn't converge, or add error handling)
    try:
        scores = nx.pagerank(nx_graph, max_iter=200)
    except nx.PowerIterationFailedConvergence:
        # Fallback to degree centrality if PageRank fails to converge
        scores = nx.degree_centrality(nx_graph)

    top_indices = sorted(scores, key=scores.get, reverse=True)[:num_sentences]
    top_indices.sort()
    
    summary = " ".join([sentences[i] for i in top_indices])
    
    # Extract keywords using TF-IDF sums as a simple byproduct helper
    feature_names = vectorizer.get_feature_names_out()
    tfidf_sums = np.asarray(tfidf_matrix.sum(axis=0)).ravel()
    keyword_scores = [(feature_names[i], tfidf_sums[i]) for i in range(len(feature_names))]
    top_keywords = [word for word, score in sorted(keyword_scores, key=lambda x: x[1], reverse=True)[:15]]
    
    return summary, scores, top_keywords


def summarize_lsa(sentences, num_sentences):
    """
    Summarizes text using Latent Semantic Analysis (LSA) via Sumy.
    """
    if not sentences:
        return "", {}, []
    
    text = " ".join(sentences)
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    stemmer = Stemmer("english")
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words("english")
    
    sumy_summary_sentences = summarizer(parser.document, num_sentences)
    summary_list = [str(s) for s in sumy_summary_sentences]
    summary = " ".join(summary_list)
    
    # Re-calculate sentence scores to match the visual requirements
    # Sumy doesn't expose clean individual scores directly in LsaSummarizer,
    # so we assign 1.0 for selected sentences, 0.1 for others for the graph visualization.
    sentence_scores = {}
    for i, sent in enumerate(sentences):
        sentence_scores[i] = 1.0 if sent in summary_list else 0.1
        
    # Extract keywords from LSA vectorizer as fallback (using custom mini TF-IDF)
    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(sentences)
        feature_names = vectorizer.get_feature_names_out()
        tfidf_sums = np.asarray(tfidf_matrix.sum(axis=0)).ravel()
        keyword_scores = [(feature_names[i], tfidf_sums[i]) for i in range(len(feature_names))]
        top_keywords = [word for word, score in sorted(keyword_scores, key=lambda x: x[1], reverse=True)[:15]]
    except ValueError:
        top_keywords = []

    return summary, sentence_scores, top_keywords


def highlight_keywords(text, keywords, color="#fde047"):
    """
    Highlights keywords in the text with a background color using html markup.
    Only highlights whole words to avoid sub-word highlighting issues.
    """
    if not text or not keywords:
        return text

    highlighted_text = text
    
    # Sort keywords by length in descending order to avoid highlighting subsets of longer keywords first
    sorted_keywords = sorted(keywords, key=len, reverse=True)
    
    for kw in sorted_keywords:
        if len(kw) < 3: # Skip very short keywords (like 'an', 'it')
            continue
            
        # Case-insensitive word boundary match
        pattern = re.compile(r'\b(' + re.escape(kw) + r')\b', re.IGNORECASE)
        
        # Replace matches with styled spans
        highlighted_text = pattern.sub(f'<span style="background-color: {color}; color: black; font-weight: 500; px-1; border-radius: 4px;">\\1</span>', highlighted_text)
        
    return highlighted_text
