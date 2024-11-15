import streamlit as st
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import tensorflow as tf
import json
import pandas as pd

# Load the warbler facts DataFrame
warbler_facts_df = pd.read_csv('Fun Facts about Warblers.csv')

# Define the introductory text to identify and any unwanted placeholder text
intro_prefix = "Here are five unique, fun, and interesting facts about"
placeholder_text = "No fact available for this fun fact slot."

# Function to clean up the introductory text and placeholder text in the DataFrame
def clean_facts(df):
    for col in [f'Fun Fact {i}' for i in range(1, 6)]:
        # Replace introductory text and placeholder with "No fact available"
        df[col] = df[col].apply(lambda x: "No fact available" if pd.isna(x) or
                                 (isinstance(x, str) and (x.startswith(intro_prefix) or placeholder_text in x)) else x)
    return df

# Apply the cleaning function to the DataFrame
warbler_facts_df = clean_facts(warbler_facts_df)

# Function to get all fun facts for a species from the DataFrame
def get_fun_facts(species_name):
    fact_row = warbler_facts_df[warbler_facts_df['Species Name'] == species_name]
    if not fact_row.empty:
        facts = [fact_row[f'Fun Fact {i}'].values[0] for i in range(1, 6)]  # Get facts from columns Fun Fact 1 to Fun Fact 5
        return facts
    else:
        return ["No facts available for this warbler."]

# Page configuration
st.set_page_config(page_title="Warbler Classifier", page_icon="🐦", layout="centered")

# Title and prompt for users
st.title('Warbler Classification Application')
st.markdown("### 📸 Please upload a warbler image for classification.")
st.divider()

# Sidebar with information
st.sidebar.title("About This App")
st.sidebar.write("This app classifies warbler images and provides interesting facts about them.")
st.sidebar.markdown("### Instructions")
st.sidebar.write("1. Upload an image of a warbler.\n2. View the predicted species and learn some fun facts!")

# Load the model
model = load_model('warbler_model.keras')

# Load class names
with open('class_order.json', 'r') as f:
    class_names_ordered = json.load(f)

# Preprocess image function
def preprocess_image(image):
    # Convert image to RGB if it has an alpha channel or other mode
    image = image.convert("RGB")
    image = image.resize((224, 224))  # Resize to match the model's expected dimensions
    image = np.array(image) / 255.0  # Normalize pixel values
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

# Helper function to clean up the species name by removing numbers, periods, and extra whitespace
def clean_species_name(species_name):
    # Remove any leading numbers, periods, and whitespace
    cleaned_name = ''.join([char for char in species_name if not char.isdigit()]).replace('.', '').strip()
    return cleaned_name

# File uploader
uploaded_file = st.file_uploader("Choose a photo", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display uploaded image
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    # Preprocess and predict
    image = Image.open(uploaded_file)
    processed_image = preprocess_image(image)

    with st.spinner("Classifying..."):
        predictions = model.predict(processed_image)
    predicted_class = np.argmax(predictions, axis=1)[0]
    raw_species_name = class_names_ordered[predicted_class]
    cleaned_species_name = clean_species_name(raw_species_name)

    st.success(f"Predicted warbler: **{cleaned_species_name}**")

    # Display the fun facts
    fun_facts = get_fun_facts(cleaned_species_name)

    # Filter out invalid facts and handle NaNs
    valid_facts = []
    for fact in fun_facts:
        if isinstance(fact, str):  # Ensure the fact is a string
            if fact != "No fact available":  # Exclude placeholder text
                cleaned_fact = fact.split('. ', 1)[1] if '. ' in fact else fact  # Clean the fact
                valid_facts.append(cleaned_fact)
        elif not pd.isna(fact):  # Handle non-string and NaN values
            valid_facts.append("No fact available for this fun fact slot.")

# Display the valid fun facts or a message if none are available
    if valid_facts:
        for i, fact in enumerate(valid_facts, start=1):
            st.markdown(f"### 🌟 Fun Fact {i}: {fact}")
    else:
        st.markdown("### 🌟 No fun facts available for this warbler.")
 