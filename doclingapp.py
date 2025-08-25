import os
# Atur lokasi cache HuggingFace agar aman di Streamlit Cloud
os.environ["HF_HOME"] = "/tmp/huggingface"

import streamlit as st
from docling.document_converter import DocumentConverter
from pathlib import Path
import tempfile
import zipfile
import io

st.title("📑 Pembaca Multi Dokumen Akurat dengan Docling")
st.write("Unggah beberapa file PDF, DOCX, XLSX, atau PPTX → hasil bisa dipilih dalam **Markdown (.md)** atau **Text (.txt)**")

# Inisialisasi converter sekali saja
if "converter" not in st.session_state:
    st.session_state.converter = DocumentConverter()

# Pilihan format output
st.subheader("⚙️ Pilih Format Output")
output_md = st.checkbox("Markdown (.md)", value=True)
output_txt = st.checkbox("Text (.txt)", value=True)

if not (output_md or output_txt):
    st.warning("Silakan pilih minimal satu format output (Markdown atau Text).")

# Fungsi ekstraksi dengan progress bar
def convert_file_with_progress(file_bytes, filename, progress, step, total):
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp_dir:
        file_path = Path(tmp_dir) / filename
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        # Update progress bar
        pct = int((step / total) * 100)
        progress.progress(pct, text=f"Memproses {filename} ({step}/{total})...")

        # Konversi dokumen
