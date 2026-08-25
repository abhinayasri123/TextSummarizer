import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Apply basic styling for plots
sns.set_theme(style="whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']

def plot_word_frequency(tokens_df, num_words=15):
    """
    Plots a horizontal bar chart of the top N word frequencies,
    ignoring stopwords, punctuation, and converting to lowercase.
    """
    # Filter out punctuation, whitespace, and stopwords
    filtered_tokens = tokens_df[
        (~tokens_df['Is_Stopword']) & 
        (~tokens_df['Is_Punctuation']) & 
        (tokens_df['Is_Alpha'])
    ].copy()
    
    # Normalize word forms using Lemma
    filtered_tokens['Word'] = filtered_tokens['Lemma'].str.lower()
    
    # Calculate word counts
    word_counts = filtered_tokens['Word'].value_counts().head(num_words)
    
    if word_counts.empty:
        # Return empty plot figure
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No words available to display frequency.", ha='center', va='center')
        ax.axis('off')
        return fig
        
    df_plot = pd.DataFrame({'Word': word_counts.index, 'Frequency': word_counts.values})
    
    # Initialize figure
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    # Color palette
    colors = sns.color_gradient = sns.color_palette("plasma", len(df_plot))
    
    # Create horizontal bar plot
    bars = sns.barplot(
        x='Frequency', 
        y='Word', 
        data=df_plot, 
        palette=colors,
        hue='Word',
        legend=False,
        ax=ax
    )
    
    # Adjust aesthetics
    ax.set_title(f"Top {num_words} Most Frequent Words (Lemmatized)", fontsize=14, fontweight='bold', pad=15, color='#1e293b')
    ax.set_xlabel("Frequency Count", fontsize=11, fontweight='semibold', color='#475569')
    ax.set_ylabel("", fontsize=11)
    ax.tick_params(axis='both', colors='#475569')
    
    # Add counts on top of bars
    for bar in bars.patches:
        width = bar.get_width()
        ax.text(
            width + 0.1, 
            bar.get_y() + bar.get_height() / 2, 
            f'{int(width)}', 
            ha='left', 
            va='center', 
            fontsize=10, 
            color='#1e293b', 
            fontweight='bold'
        )
        
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    
    return fig


def plot_sentence_importance(sentence_scores, summary_indices):
    """
    Plots a line-chart of sentence scores by sentence index.
    Highlighting the sentences selected for the summary.
    """
    if not sentence_scores:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, "No sentences available for importance graph.", ha='center', va='center')
        ax.axis('off')
        return fig

    # Prepare indices and scores sorted chronologically
    indices = sorted(sentence_scores.keys())
    scores = [sentence_scores[i] for i in indices]
    
    fig, ax = plt.subplots(figsize=(9, 4.5))
    
    # Plot line showing general structure
    ax.plot(indices, scores, color='#cbd5e1', linestyle='-', linewidth=2, label='Sentence Flow')
    
    # Highlight non-summary sentence markers
    non_summary_indices = [i for i in indices if i not in summary_indices]
    non_summary_scores = [sentence_scores[i] for i in non_summary_indices]
    ax.scatter(non_summary_indices, non_summary_scores, color='#94a3b8', s=40, zorder=2, alpha=0.7)
    
    # Highlight summary sentence markers
    summary_scores = [sentence_scores[i] for i in summary_indices]
    ax.scatter(
        summary_indices, 
        summary_scores, 
        color='#6366f1', 
        s=120, 
        marker='*', 
        zorder=3, 
        label='Selected for Summary',
        edgecolor='#4f46e5',
        linewidth=1
    )
    
    # Adjust details
    ax.set_title("Sentence Importance & Summary Distribution", fontsize=14, fontweight='bold', pad=15, color='#1e293b')
    ax.set_xlabel("Sentence Position in Document (Index)", fontsize=11, fontweight='semibold', color='#475569')
    ax.set_ylabel("Importance Score", fontsize=11, fontweight='semibold', color='#475569')
    ax.tick_params(axis='both', colors='#475569')
    ax.set_xticks(indices)
    
    # Handle massive documents (prune x-ticks if too long)
    if len(indices) > 20:
        step = len(indices) // 10
        ax.set_xticks(indices[::step])
        
    ax.legend(frameon=True, facecolor='white', edgecolor='#e2e8f0', loc='upper right')
    sns.despine()
    plt.tight_layout()
    
    return fig


def plot_summary_stats_comparison(original_words, summary_words):
    """
    Plots a side-by-side or stacked metric chart of original vs summary metrics.
    """
    fig, ax = plt.subplots(figsize=(6, 3))
    categories = ['Original Words', 'Summary Words']
    values = [original_words, summary_words]
    
    # Set colors
    colors = ['#94a3b8', '#6366f1']
    
    # Draw bars
    bars = ax.barh(categories, values, color=colors, height=0.5, edgecolor='none')
    
    # Label inside or next to bars
    for bar in bars:
        width = bar.get_width()
        ax.text(
            width / 2 if width > original_words * 0.15 else width + 5,
            bar.get_y() + bar.get_height() / 2,
            f'{int(width)}',
            ha='center' if width > original_words * 0.15 else 'left',
            va='center',
            color='white' if width > original_words * 0.15 else '#1e293b',
            fontweight='bold',
            fontsize=11
        )
        
    ax.set_title("Word Reduction Impact", fontsize=12, fontweight='bold', color='#1e293b', pad=10)
    ax.set_xlabel("Total Word Count", fontsize=9, color='#475569')
    ax.tick_params(axis='y', labelsize=10, colors='#1e293b')
    ax.grid(False)
    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    
    return fig
