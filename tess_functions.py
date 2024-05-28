import os
import requests
import pytesseract

import streamlit as st

def check_tesseract():
    tesseract_cmd = tesseract_path()

    if tesseract_cmd:
        #st.write(f"Tesseract available at: {tesseract_cmd}")
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    else:
        st.error("Tesseract is not installed or not found in the common paths.")
        

# Find the Tesseract command
def tesseract_path():
    possible_paths = [
        '/usr/bin/tesseract',  # Common Linux path
        '/usr/local/bin/tesseract',  # Common alternate path
        '/opt/homebrew/bin/tesseract',  # Homebrew path (macOS)
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None


def download_tessdata():
    languages = ['eng', 'mya']
    tessdata_dir = 'tessdata' 
    """
    Download Tesseract language files if they are not already present in the tessdata directory.
    
    :param languages: List of language codes to download, e.g., ['eng', 'osd', 'mya']
    :param tessdata_dir: Directory where the Tesseract tessdata files should be stored
    """
    # Ensure the tessdata directory exists
    os.makedirs(tessdata_dir, exist_ok=True)

    # GitHub base URL for your tessdata files
    base_url = "https://raw.githubusercontent.com/nchanko/Myanmar-Ebook-OCR/44c4777dbfcf744390c5081c6341b11499499bf6/Tesseract-OCR/tessdata"
    
    # Iterate over each language and download if not exists
    for lang in languages:
        lang_file = f"{lang}.traineddata"
        destination_path = os.path.join(tessdata_dir, lang_file)
        
        # Check if the language data file already exists
        if not os.path.exists(destination_path):
            # Download the language data file
            url = f"{base_url}/{lang_file}"
            try:
                print(f"Downloading {lang_file}...")
                response = requests.get(url)
                response.raise_for_status()  # Check if the download was successful
                
                # Write the downloaded file to the destination path
                with open(destination_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {lang_file} successfully.")
            except requests.exceptions.RequestException as e:
                print(f"Failed to download {lang_file}: {e}")

