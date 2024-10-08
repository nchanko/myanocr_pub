
Version 1.1
- PDF crop
- Epub Converter
---- 
Version 1.0
Initial realease
- OCR
- Font Converter
# OCR App Setup Guide

This README provides instructions on how to set up and run the OCR application on macOS. Users of Windows or Linux can follow these instructions with minor adjustments.

## Prerequisites

Ensure that Python (version 3.6 or later) is installed on your system. If not, download and install it from [python.org](https://python.org).

## Create Google Cloud Vision Service Account.
You need to replace cloud_vision_service_acc.json with your own credentials. 
Ref: [https://daminion.net/docs/how-to-get-google-cloud-vision-api-key/](https://daminion.net/docs/how-to-get-google-cloud-vision-api-key/)


## Step 1: Clone the Repository

First, clone the OCR application repository from GitHub. Open your terminal and execute the following command:

```bash
git clone https://github.com/nchanko/myanocr_pub.git
cd myanocr_pub
```

## Step 2: Create a Virtual Environment
It is recommended to use a virtual environment to manage and isolate the application dependencies. Use the following commands to create and activate a virtual environment:

On macOS and Linux:
```bash
python3 -m venv venv               # Create a virtual environment
source venv/bin/activate  
```   

On windows:
```bash
python -m venv venv                # Create a virtual environment
.\venv\Scripts\activate            # Activate the virtual environment
```

## Step 3: Install Dependencies
With the virtual environment activated, install the required packages specified in the requirements.txt file: You may also need to install packages separately.

```bash
pip install -r packages.txt

pip install -r requirements.txt  
```

## Step 4: Run the Application
After installing the dependencies, the application is ready to be launched. Start the OCR application using Streamlit by running the following command:
```bash
streamlit run ocr.py
```
This command will start the Streamlit server. You can access the application by navigating to http://localhost:8501 in your web browser.
