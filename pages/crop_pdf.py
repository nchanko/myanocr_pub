import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
from PyPDF2 import PdfWriter, PdfReader

def load_pdf(pdf_file):
    """Load the PDF file and return the document object."""
    return fitz.open(stream=pdf_file.read(), filetype="pdf")

def pdf_page_to_image(pdf_document, page_number, crop_box=None):
    """Convert a PDF page to an image, optionally cropped."""
    page = pdf_document.load_page(page_number)
    pix = page.get_pixmap()

    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    if crop_box:
        img = img.crop(crop_box)

    return img

def display_sample_pages(pdf_document, start_page, end_page, crop_box=None):
    """Display a range of pages of the PDF with optional cropping in two columns."""
    num_pages = len(pdf_document)
    end_page = min(end_page, num_pages)  # Ensure end_page does not exceed total pages
    cols = st.columns(2)  # Create two columns

    for i in range(start_page - 1, end_page):  # Pages are 0-indexed in PyMuPDF
        img = pdf_page_to_image(pdf_document, i, crop_box)
        col = cols[(i - start_page + 1) % 2]
        with col:
            st.image(img, caption=f"Page {i + 1}", use_column_width=True)

def main():
    st.title("PDF Crop Tool")

    # Organize PDF upload and page range selection into two columns
    col1, col2 = st.columns(2)

    with col1:
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

    if pdf_file is not None:
        pdf_document = load_pdf(pdf_file)
        max_pages = len(pdf_document)

        with col2:
            start_page, end_page = st.slider(
                "Select the page range",
                min_value=1,
                max_value=max_pages,
                value=(1, min(10, max_pages))
            )
        
        st.header("Crop Settings")

        # Organize crop settings into two columns
        col1, col2 = st.columns(2)

        with col1:
            x1 = st.number_input("Crop X1 (left)", min_value=0, max_value=int(pdf_document.load_page(0).rect.width), value=0)
            y1 = st.number_input("Crop Y1 (top)", min_value=0, max_value=int(pdf_document.load_page(0).rect.height), value=0)

        with col2:
            x2 = st.number_input("Crop X2 (right)", min_value=0, max_value=int(pdf_document.load_page(0).rect.width), value=int(pdf_document.load_page(0).rect.width))
            y2 = st.number_input("Crop Y2 (bottom)", min_value=0, max_value=int(pdf_document.load_page(0).rect.height), value=int(pdf_document.load_page(0).rect.height))

        crop_box = (x1, y1, x2, y2)

        st.header("Sample Pages (After Cropping)")
        display_sample_pages(pdf_document, start_page, end_page, crop_box)

        if st.button("Apply Cropping to PDF"):
            output_pdf = io.BytesIO()
            pdf_writer = PdfWriter()

            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap()

                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                img = img.crop(crop_box)

                # Convert cropped image to PDF page
                img_bytes = io.BytesIO()
                img.save(img_bytes, format="PDF")
                img_bytes.seek(0)

                pdf_reader = PdfReader(img_bytes)
                pdf_writer.add_page(pdf_reader.pages[0])

            pdf_writer.write(output_pdf)
            output_pdf.seek(0)

            st.success("PDF Cropping Applied!")
            st.download_button(label="Download Cropped PDF", data=output_pdf, file_name="cropped_pdf.pdf", mime="application/pdf")

if __name__ == "__main__":
    main()