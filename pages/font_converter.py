import streamlit as st
import os
from rabbit import Rabbit
rabbit = Rabbit()

def zawgyi_to_unicode(zawgyi_text):
    """Convert Zawgyi text to Unicode using the rabbit module."""
    return rabbit.zg2uni(zawgyi_text)

def convert_file_to_unicode(file):
    """Read the content of the file, convert it to Unicode, and return the result."""
    # Read the content of the file
    content = file.read()
    # Decode the content to string if it's in bytes
    if isinstance(content, bytes):
        content = content.decode('utf-8')
    # Convert the text from Zawgyi to Unicode
    unicode_content = zawgyi_to_unicode(content)
    return unicode_content

def main():
    st.sidebar.markdown(""" 
    Credit :[:red[Rabbit Converter]](https://www.rabbit-converter.org/Rabbit/) 
    """)
    st.title(':blue[Zawgyi to Unicode] Converter')

    # File uploader allows user to add their own file
    uploaded_file = st.file_uploader("Choose a file", type=['txt'],help="Select a txt file written in Zawgyi.")
    
    if uploaded_file is not None:
        # Convert the file to Unicode
        unicode_text = convert_file_to_unicode(uploaded_file)
        
        # Show the converted text in a scrollable, full-width text area
        st.text_area("Converted Text (Unicode):", unicode_text, height=300)

        # Generate the new file name
        base_name, ext = os.path.splitext(uploaded_file.name)
        new_file_name = f"{base_name}_unicode{ext}"
        
        # Let user download the converted text
        st.download_button(
            label="Download Converted Text",
            data=unicode_text.encode('utf-8'),
            file_name=new_file_name,
            mime='text/plain'
        )

if __name__ == "__main__":
    main()
