import streamlit as st
import pytesseract
from pdf2image import convert_from_path, pdfinfo_from_path
from PIL import Image
import tempfile
from google.cloud import vision

from dotenv import load_dotenv
import io
import os
import shutil

# Load environment variables
load_dotenv()

# Functions for downloading Tesseract data and checking installation
from tess_functions import download_tessdata, check_tesseract

# Download necessary tessdata files
download_tessdata()
tessdata_dir = 'tessdata' 

# Function to find Poppler path
def get_poppler_path():
    possible_paths = [
        '/usr/local/bin',     # Common on macOS and some Linux setups
        '/usr/bin',           # Default on many Linux systems
        '/opt/homebrew/bin',  # Homebrew on newer Macs
        'C:\\Program Files\\poppler\\bin'  # Common on Windows
    ]
    for path in possible_paths:
        if os.path.isfile(os.path.join(path, 'pdftoppm')):
            return path
    return None

def pdf_to_images(pdf_path, limit=None):
    poppler_path = get_poppler_path()
    if not poppler_path:
        raise FileNotFoundError("Poppler not found. Install it or check your installation.")
    
    info = pdfinfo_from_path(pdf_path, userpw=None, poppler_path=poppler_path)
    max_pages = min(info['Pages'], limit if limit is not None else info['Pages'])
    max_pages = min(max_pages, 20)  # Enforce the maximum limit of 20 pages
    
    return convert_from_path(pdf_path, dpi=300, first_page=1, last_page=max_pages, poppler_path=poppler_path)

def ocr_with_tesseract(image, languages):
    lang = "+".join(languages)
    custom_config = f'--tessdata-dir {tessdata_dir} -l {lang}'
    return pytesseract.image_to_string(image, config=custom_config)

def ocr_with_google(image_path):
    client = vision.ImageAnnotatorClient()
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    return response.text_annotations[0].description if response.text_annotations else ""

def split_pages(image):
    # Split the image into two pages
    width, height = image.size
    mid_width = width // 2
    left_image = image.crop((0, 0, mid_width, height))
    right_image = image.crop((mid_width, 0, width, height))
    return [left_image, right_image]

def main():
    st.sidebar.markdown("Developed by [Nyein Chan Ko Ko](https://www.linkedin.com/in/nyeinchankoko/)")
    st.title(":blue_book: PDF and Image OCR Tool")

    uploaded_file = st.file_uploader("Upload a PDF or Image file", type=["pdf", "png", "jpg", "jpeg"], help="Upload a pdf or image file")
    language_mapping = {"English": "eng", "Myanmar": "mya"}
    available_languages = list(language_mapping.keys())
    selected_language_names = st.multiselect("Select OCR Languages", available_languages, default="English", help="Select the language for Tesseract model. If the document contains both English and Myanmar, choose Myanmar first then English.")
    selected_languages = [language_mapping[name] for name in selected_language_names]
    ocr_engine = st.selectbox("Select OCR Engine", ["Google OCR", "Tesseract"], help="Select OCR model, Google is better.")
    page_limit = st.number_input("Limit number of pages to process (set 0 for no limit)", min_value=0, value=10, help="As for trial, Only 10 pages are allowed as maximum. Use these websites to split pdf files. https://smallpdf.com")
    two_pages_per_scan = st.checkbox("Check if each scan might have two pages side by side", value=False)

    process_button = st.button("Process PDF", help="Click to process PDF file")
    cancel_button = st.button("Cancel")

    if process_button and uploaded_file:
        
        with st.spinner('Processing...'):
            try:
                # Determine the file type
                if uploaded_file.type == "application/pdf":
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        tmp_file_path = os.path.join(tmp_dir, "tempfile.pdf")
                        with open(tmp_file_path, 'wb') as f:
                            f.write(uploaded_file.getvalue())
                        
                        st.success("✅ Loaded PDF file and saved temporarily...")
                        pdf_pages = pdf_to_images(tmp_file_path, limit=page_limit if page_limit > 0 else None)
                        st.success(f"✅ Converted PDF to images, processing {len(pdf_pages)} pages...")

                        all_text = []
                        progress_bar = st.progress(0)
                        progress_text = st.empty()

                        for i, page in enumerate(pdf_pages):
                            if cancel_button:
                                st.error("Processing cancelled by user.")
                                break

                            if two_pages_per_scan:
                                images_to_process = split_pages(page)
                            else:
                                images_to_process = [page]

                            for split_page in images_to_process:
                                image_path = os.path.join(tmp_dir, f"page_{i + 1}.jpg")
                                split_page.save(image_path, 'JPEG')
                                text = ocr_with_tesseract(Image.open(image_path), selected_languages) if ocr_engine == "Tesseract" else ocr_with_google(image_path)
                                all_text.append(text)

                                # Update progress and display current page processing
                                progress = (i + 1) / len(pdf_pages)
                                progress_bar.progress(progress)
                                progress_text.text(f"Processing page {i + 1}/{len(pdf_pages)}...")
                        
                        st.session_state.ocr_text = "\n".join(all_text)
                else:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        st.success("✅ Loaded image and saved temporarily...")
                        
                        if two_pages_per_scan:
                            original_image = Image.open(tmp_file.name)
                            images_to_process = split_pages(original_image)
                        else:
                            images_to_process = [Image.open(tmp_file.name)]

                        all_text = []
                        for img in images_to_process:
                            text = ocr_with_tesseract(img, selected_languages) if ocr_engine == "Tesseract" else ocr_with_google(tmp_file.name)
                            all_text.append(text)

                        st.session_state.ocr_text = "\n".join(all_text)

            except Exception as e:
                if "credential" in str(e).lower():
                    st.error(f"Credential error: Please check your Google Cloud credentials. Try this instruction to apply Google service acc. https://daminion.net/docs/how-to-get-google-cloud-vision-api-key/")
                else:
                    st.error(f"An error occurred: {e}")
            finally:
                if 'cancel' in st.session_state:
                    del st.session_state['cancel']

    if st.session_state.get('ocr_text'):
        st.text_area("OCR Output", st.session_state.ocr_text, height=250)
        st.download_button("Download Text", data=st.session_state.ocr_text, file_name="ocr_output.txt", mime="text/plain")

if __name__ == "__main__":
    main()
