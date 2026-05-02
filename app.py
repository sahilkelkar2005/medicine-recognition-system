import os
from flask import Flask, request, render_template
from PIL import Image
import easyocr
import numpy as np
import re

app = Flask(__name__)

# Load OCR model once
reader = easyocr.Reader(['en'])

# 🔍 Extract text from image
def extract_text(image):
    img = np.array(image)
    results = reader.readtext(img)

    text = " ".join([res[1] for res in results])
    return text.lower()

# 🧠 Detect if it's medicine
def is_medicine(text):
    keywords = [
        "tablet", "capsule", "mg", "paracetamol",
        "ibuprofen", "syrup", "dose", "pharma",
        "dolo", "crocin", "strip"
    ]
    return any(word in text for word in keywords)

# 🧾 Extract structured info (IMPROVED)
def extract_medicine_info(text):
    # Find strength (e.g., 500 mg)
    strength_match = re.search(r'\b\d+\s?mg\b', text)
    strength = strength_match.group() if strength_match else "Not found"

    # Known medicine names
    medicine_keywords = [
        "paracetamol", "ibuprofen", "dolo", "crocin",
        "aspirin", "cetirizine", "amoxicillin",
        "azithromycin", "metformin", "pantoprazole"
    ]

    medicine_name = "Not found"

    for word in text.split():
        if word in medicine_keywords:
            medicine_name = word
            break

    # Detect type
    if "tablet" in text:
        mtype = "Tablet"
    elif "capsule" in text:
        mtype = "Capsule"
    elif "syrup" in text:
        mtype = "Syrup"
    else:
        mtype = "Unknown"

    return {
        "name": medicine_name.upper(),
        "strength": strength,
        "type": mtype
    }

# 🌐 Main route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', raw_text=None)

        # Open image
        image = Image.open(file)

        # Step 1: OCR
        text = extract_text(image)

        # Step 2: Check medicine
        if is_medicine(text):
            info = extract_medicine_info(text)

            return render_template(
                'index.html',
                detected=True,
                name=info["name"],
                strength=info["strength"],
                mtype=info["type"],
                raw_text=text
            )
        else:
            return render_template(
                'index.html',
                detected=False,
                raw_text=text
            )

    return render_template('index.html', raw_text=None)

# 🚀 Run app
if __name__ == '__main__':
    app.run(debug=True)