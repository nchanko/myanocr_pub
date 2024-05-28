import streamlit as st

def about():

    # Read the markdown file
    st.image("demo.png",caption = "OCR Myanmar Book.",)
    with open("about.md", "r") as f:
        markdown_text = f.read()

    # Display the markdown text on the page
    st.markdown(markdown_text)

about()
