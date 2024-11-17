# Import libraries
from transformers import pipeline
import pandas as pd

# Load dataset
warbler_facts_df = pd.read_csv('Fun Facts about Warblers.csv')

# Pretrained summarization pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Function to clean and prepare text for summarization
def prepare_text_for_summary(species_name, warbler_facts_df):
    # Fetch the row for the given species
    fact_row = warbler_facts_df[warbler_facts_df['Species Name'] == species_name]
    
    if fact_row.empty:
        return "No fun facts available to summarize."

    # Combine all available fun facts into a single text block
    fun_facts = " ".join(
        fact_row[f"Fun Fact {i}"].values[0]
        for i in range(1, 6)
        if pd.notna(fact_row[f"Fun Fact {i}"].values[0]) and
        fact_row[f"Fun Fact {i}"].values[0] != "No fact available"
    )
    
    if not fun_facts.strip():
        return "No fun facts available to summarize."

    return fun_facts

# Function to fix incomplete summaries
def fix_incomplete_summary(summary):
    """
    Checks for common incomplete sentence patterns and fixes or annotates them.
    """
    if summary.endswith(('in the', 'and', 'such as', 'with')):
        return summary + " Additional context may be required."
    return summary

# Function to refine the summary for key ecological or behavioral aspects
def refine_summary(summary, facts_df, species_name):
    # Retrieve key ecological and behavioral facts from the dataset
    fact_row = facts_df[facts_df['Species Name'] == species_name]
    if not fact_row.empty:
        key_facts = [
            fact_row[f'Fun Fact {i}'].values[0]
            for i in range(1, 6)
            if "habitat" in fact_row[f'Fun Fact {i}'].values[0].lower()
        ]
    else:
        key_facts = []
    
    # If no ecological/behavioral facts are in the summary, append one
    if key_facts and not any("habitat" in summary.lower() for fact in key_facts):
        summary += f" Additionally, {key_facts[0]}"  # Add the first relevant fact.
    
    return summary

# Summarize fun facts for a given species
def summarize_facts(species_name, warbler_facts_df):
    text = prepare_text_for_summary(species_name, warbler_facts_df)
    if text == "No fun facts available to summarize.":
        return text
    
    # Perform summarization
    summary = summarizer(text, max_length=70, min_length=30, do_sample=True, temperature=0.7)
    
    # Apply post-processing to the summary
    cleaned_summary = fix_incomplete_summary(summary[0]['summary_text'])
    refined_summary = refine_summary(cleaned_summary, warbler_facts_df, species_name)
    return refined_summary