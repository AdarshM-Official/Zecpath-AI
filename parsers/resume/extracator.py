import fitz  # PyMuPDF
from docx import Document
import re
import json
import os
from datetime import datetime


def read_pdf(path):
    text = ""

    doc = fitz.open(path)

    for page in doc:
        text += page.get_text("text") + "\n"

    return text

def read_docx(path):
    doc = Document(path)

    text = "\n".join([para.text for para in doc.paragraphs])

    return text


def read_resume(file_path):

    if file_path.endswith(".pdf"):
        return read_pdf(file_path)

    elif file_path.endswith(".docx"):
        return read_docx(file_path)

    else:
        raise ValueError("❌ Unsupported file format")

def clean_text(text):

    # Remove weird unicode characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    # Normalize line breaks
    text = re.sub(r'\n+', '\n', text)

    return text.strip()


def normalize_text(text):

    lines = text.split("\n")

    normalized = []

    for line in lines:

        line = line.strip()

        # Normalize bullet points
        line = re.sub(r'^[•●▪■◆➤►-]+', '-', line)

        # Normalize headings
        if line.isupper() and len(line.split()) <= 5:
            line = line.title()

        normalized.append(line)

    return "\n".join(normalized)


def fix_layout(text):

    # Remove excessive spacing from columns/tables
    text = re.sub(r'\s{3,}', ' ', text)

    # Merge broken lines
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    return text


def save_output(data, output_path='data/output/res_extract_op.txt'):

    output = {
        "timestamp": str(datetime.now()),
        "cleaned_text": data
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4)

    print(f"✅ Saved: {output_path}")


def extract_resume(file_path):

    print(f"\n📄 Processing: {file_path}")

    # Step 1: Read Resume
    raw_text = read_resume(file_path)

    # Step 2: Clean Text
    cleaned_text = clean_text(raw_text)

    # Step 3: Fix Layout
    fixed_text = fix_layout(cleaned_text)

    # Step 4: Normalize
    normalized_text = normalize_text(fixed_text)

    return normalized_text

def process_all_resumes(input_folder, output_folder):

    os.makedirs(output_folder, exist_ok=True)

    logs = []

    for file_name in os.listdir(input_folder):

        file_path = os.path.join(input_folder, file_name)

        try:

            extracted_text = extract_resume(file_path)

            # Save JSON
            output_file = os.path.join(
                output_folder,
                file_name.split(".")[0] + ".json"
            )

            save_output(extracted_text, output_file)

            logs.append(f"{file_name} --> SUCCESS")

        except Exception as e:

            logs.append(f"{file_name} --> FAILED ({str(e)})")

    # Save Logs
    with open("tests/test_logs.txt", "w") as log_file:

        for log in logs:
            log_file.write(log + "\n")

    print("\n🧪 Test logs saved: test_logs.txt")

if __name__ == "__main__":

    INPUT_FOLDER = "aiproject/data/resumes"
    OUTPUT_FOLDER = "aiproject/data/cleaned_resumes"

    process_all_resumes(INPUT_FOLDER, OUTPUT_FOLDER)