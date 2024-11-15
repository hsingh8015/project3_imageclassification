# Uncomment the following code if you are using Colab.
#pip install gradio

#Import libraries
import gradio as gr
import numpy as np
from PIL import Image
from keras.models import load_model
from keras.preprocessing import image

# Load the trained Keras model
model = load_model('warbler_model.keras', compile=False)

# Define the prediction function
def predict_species(img):
    # Preprocess the image
    img = img.resize((224, 224))  # Resize to image size that the model expects
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    img_array /= 255.0  # Normalize the image

# Make predictions
predictions = model.predict(img_array)
predicted_class = np.argmax(predictions, axis=1)