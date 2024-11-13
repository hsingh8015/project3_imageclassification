import streamlit as st
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import tensorflow as tf
import json
# from warbler_data import warbler_facts  # Update to the correct facts file name

# Page configuration
st.set_page_config(page_title="Warbler Classifier", page_icon="🐦", layout="centered")

# Title and prompt for users
st.title('Warbler Classification Application')
st.markdown("### 📸 Please upload a warbler image for classification.")
st.divider()

# Sidebar with information
st.sidebar.title("About This App")
st.sidebar.write("This app classifies warbler images with ?% accuracy and provides interesting facts about them.")
st.sidebar.markdown("### Instructions")
st.sidebar.write("1. Upload an image of a warbler.\n2. View the predicted species and learn some fun fact!")

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
    st.success("Classification complete!")

    # Get predicted class and corresponding fact
    predicted_class = np.argmax(predictions, axis=1)
    warbler_name = class_names_ordered[predicted_class[0]]
    # warbler_fact = warbler_facts.get(warbler_name, "No fact available for this warbler.")

    # Display results in two columns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"### Predicted warbler: **{warbler_name}**")
    # with col2:
    #     st.markdown(f"### 🌟 Fun Fact: {warbler_fact}")