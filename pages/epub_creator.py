import streamlit as st
from ebooklib import epub
import os

def create_epub_with_embedded_font(title, author, text, output_file, font_path, cover_image=None):
    # Create the book
    book = epub.EpubBook()

    # Set metadata
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)

    if cover_image is not None:
        # Add cover image from UploadedFile directly
        book.set_cover("cover.jpg", cover_image.read())

    # Create a chapter
    chapter = epub.EpubHtml(title='Chapter 1', file_name='chapter_1.xhtml', lang='en')
    chapter.content = f'<html><head><link rel="stylesheet" type="text/css" href="style/style.css"/></head><body><h1>{title}</h1><p>{text}</p></body></html>'
    book.add_item(chapter)

    # Embed the custom font
    font_name = os.path.basename(font_path)
    font_type = 'application/vnd.ms-opentype' if font_path.endswith('.otf') else 'application/font-woff'
    book.add_item(epub.EpubItem(uid='font', file_name=f'fonts/{font_name}', media_type=font_type, content=open(font_path, 'rb').read()))

    # Create the CSS to use the custom font
    style = f'''
    @font-face {{
        font-family: "CustomFont";
        src: url("../fonts/{font_name}");
    }}
    body {{
        font-family: "CustomFont";
    }}
    '''
    style_item = epub.EpubItem(uid="style", file_name="style/style.css", media_type="text/css", content=style)
    book.add_item(style_item)

    # Link the style to the chapter
    chapter.add_item(style_item)

    # Add default NCX and Nav files
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Define Table Of Contents
    book.toc = (epub.Link('chapter_1.xhtml', 'Chapter 1', 'chapter_1'),)

    # Add book spine
    book.spine = ['nav', chapter]

    # Create the EPUB file
    epub.write_epub(output_file, book, {})

def main():
    st.title("EPUB Creator")

    # Create two columns
    col1, col2 = st.columns(2)

    with col1:
        text_file = st.file_uploader("Choose a text file", type=["txt"], help="Upload unicode text file.")
        title = st.text_input("Title", "My Sample Book")
        author = st.text_input("Author", "Author Name")

    with col2:
        font_options = {
            "Pyidaungsu": "Pyidaungsu-2.5.3_Regular.ttf",
            "MUA Office": "MUA_Office_adobe.ttf"  # Default font
            # Add more font options here if needed
        }
        font_choice = st.selectbox("Select Font", list(font_options.keys()))
        font_path = font_options[font_choice]

        cover_image = st.file_uploader("Choose a cover image", type=["jpg", "jpeg", "png"],help="Upload cover image , this is optional")

    if st.button("Build EPUB"):
        if text_file is not None:
            with st.spinner('Building EPUB...'):
                text = text_file.read().decode('utf-8')
                output_file = f"{title}.epub"

                # Create the EPUB with the custom font
                create_epub_with_embedded_font(title, author, text, output_file, font_path, cover_image)

                st.success(f'EPUB file created: {output_file}')

                # Provide a download link
                with open(output_file, "rb") as file:
                    btn = st.download_button(
                        label="Download EPUB",
                        data=file,
                        file_name=output_file,
                        mime="application/epub+zip"
                    )

if __name__ == '__main__':
    main()