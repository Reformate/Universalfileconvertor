import streamlit as st
from markitdown import MarkItDown
import os
import tempfile

# Configuration for the conversion engine
# Note: MarkItDown uses requests internally for URL-based content. 
# While this app focuses on uploads, we initialize the engine here.
md = MarkItDown()

def get_converted_filename(original_name, extension):
    """Generates the new filename based on the original name."""
    base_name = os.path.splitext(original_name)[0]
    return f"{base_name}_converted.{extension}"

# --- UI Setup ---
st.set_page_config(page_title="Universal Document Reader", page_icon="📄")

st.title("📄 Universal Document Reader")
st.markdown("""
Convert your Office docs, PDFs, and HTML files into clean **Markdown** or **Plain Text** instantly.
""")

# --- [2] Upload Area ---
uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    type=["docx", "xlsx", "pptx", "pdf", "html", "zip"], 
    accept_multiple_files=True
)

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.write("---")
        st.subheader(f"Processing: {uploaded_file.name}")
        
        try:
            # [3] Resilience: Use a temporary file to bridge Streamlit memory to MarkItDown
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            # Perform the conversion
            # We wrap this in a timeout-simulated logic if it were a web request, 
            # but for local files, MarkItDown is direct.
            result = md.convert(tmp_path)
            converted_text = result.text_content
            
            # Clean up temp file
            os.remove(tmp_path)

            # [2] Instant Preview (Scrollable box)
            st.text_area(
                label="Content Preview", 
                value=converted_text, 
                height=300, 
                key=f"preview_{uploaded_file.name}"
            )

            # [2] Download Options
            col1, col2 = st.columns(2)
            
            with col1:
                md_filename = get_converted_filename(uploaded_file.name, "md")
                st.download_button(
                    label="📥 Download as Markdown (.md)",
                    data=converted_text,
                    file_name=md_filename,
                    mime="text/markdown",
                    key=f"md_{uploaded_file.name}"
                )

            with col2:
                txt_filename = get_converted_filename(uploaded_file.name, "txt")
                st.download_button(
                    label="📥 Download as Text (.txt)",
                    data=converted_text,
                    file_name=txt_filename,
                    mime="text/plain",
                    key=f"txt_{uploaded_file.name}"
                )

        except Exception as e:
            # [3] Resilience: Polite Error Handling
            st.error(f"⚠️ Could not read **{uploaded_file.name}**. Please check the format.")
            # Optional: st.exception(e) # Uncomment for debugging

else:
    st.info("Please upload one or more files to begin.")

# Footer info
st.sidebar.title("Settings & Info")
st.sidebar.info("""
**Supported Formats:**
- Word (.docx)
- Excel (.xlsx)
- PowerPoint (.pptx)
- PDF
- HTML
- ZIP (Recursive)
""")
