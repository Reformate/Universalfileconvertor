import streamlit as st
from markitdown import MarkItDown
import os
import tempfile

# Initialize the engine
md = MarkItDown()

def get_converted_filename(original_name, extension):
    base_name = os.path.splitext(original_name)[0]
    return f"{base_name}_converted.{extension}"

def format_size(bytes_size):
    """Converts bytes to a human-readable MB format."""
    return f"{bytes_size / (1024 * 1024):.2f} MB"

st.set_page_config(page_title="Universal Document Reader", page_icon="📄")
st.title("📄 Universal Document Reader")

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
            # Get original size
            original_size = uploaded_file.size
            
            # Save to temp file for processing
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                tmp_file.write(uploaded_file.read())
                tmp_path = tmp_file.name

            # Convert
            result = md.convert(tmp_path)
            
            if result and result.text_content:
                converted_text = result.text_content
                # Calculate converted size in bytes (UTF-8)
                converted_size = len(converted_text.encode('utf-8'))
                
                # --- Create Tabs ---
                tab1, tab2 = st.tabs(["📝 Content Preview", "📊 File Size Comparison"])

                with tab1:
                    st.text_area("Markdown Output", value=converted_text, height=300, key=f"p_{uploaded_file.name}")
                    
                    # Download Buttons
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button("📥 Download .md", converted_text, get_converted_filename(uploaded_file.name, "md"), "text/markdown", key=f"m_{uploaded_file.name}")
                    with col2:
                        st.download_button("📥 Download .txt", converted_text, get_converted_filename(uploaded_file.name, "txt"), "text/plain", key=f"t_{uploaded_file.name}")

                with tab2:
                    # Calculate percentage reduction
                    reduction = ((original_size - converted_size) / original_size) * 100
                    
                    # Display Table
                    st.table([
                        {"Metric": "Original File Size", "Value": format_size(original_size)},
                        {"Metric": "Converted .txt Size", "Value": format_size(converted_size)}
                    ])
                    
                    if reduction > 0:
                        st.success(f"✨ **Text version is {reduction:.1f}% smaller** than the original file.")
                    else:
                        st.info("The text version is similar or larger in size than the original source.")

            else:
                st.warning(f"⚠️ **{uploaded_file.name}** appears to be empty.")

            os.remove(tmp_path)

        except Exception as e:
            st.error(f"⚠️ Could not read **{uploaded_file.name}**.")

else:
    st.info("Please upload one or more files to begin.")
