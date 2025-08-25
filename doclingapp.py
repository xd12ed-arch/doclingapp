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

# Upload multiple files → selalu tampil
uploaded_files = st.file_uploader(
    "📂 Unggah file di sini",
    type=["pdf", "docx", "xlsx", "pptx"],
    accept_multiple_files=True
)

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
        result = st.session_state.converter.convert(file_path)
        markdown_output = result.document.export_to_markdown()

    return markdown_output

# Proses file hanya jika ada upload + format dipilih
if uploaded_files and (output_md or output_txt):
    progress = st.progress(0, text="Menunggu mulai...")
    results = {}

    try:
        with st.spinner("Mengonversi semua dokumen..."):
            total = len(uploaded_files)
            for i, uploaded_file in enumerate(uploaded_files, start=1):
                file_bytes = uploaded_file.getvalue()
                markdown_output = convert_file_with_progress(
                    file_bytes, uploaded_file.name, progress, i, total
                )

                # Nama dasar file
                input_filename = Path(uploaded_file.name).stem

                # Simpan sesuai pilihan user
                if output_md:
                    results[f"{input_filename}.md"] = markdown_output
                if output_txt:
                    results[f"{input_filename}.txt"] = markdown_output

                # Tampilkan pratinjau 20 baris pertama
                st.subheader(f"📖 Pratinjau: {uploaded_file.name}")
                preview_lines = "\n".join(markdown_output.splitlines()[:20])
                st.text(preview_lines if preview_lines.strip() else "(Dokumen kosong atau tidak terbaca)")

                # Tombol unduh per file
                if output_md:
                    st.download_button(
                        label=f"💾 Unduh {input_filename}.md",
                        data=markdown_output,
                        file_name=f"{input_filename}.md",
                        mime="text/markdown"
                    )
                if output_txt:
                    st.download_button(
                        label=f"💾 Unduh {input_filename}.txt",
                        data=markdown_output,
                        file_name=f"{input_filename}.txt",
                        mime="text/plain"
                    )

            progress.progress(100, text="Semua file selesai ✅")

        # Buat ZIP dari semua hasil
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for filename, content in results.items():
                zipf.writestr(filename, content)
        zip_buffer.seek(0)

        # Tombol unduh ZIP
        st.success("Konversi selesai! Semua file tersedia.")
        st.download_button(
            label="📦 Unduh Semua Hasil dalam ZIP",
            data=zip_buffer,
            file_name="hasil_konversi.zip",
            mime="application/zip"
        )

    except Exception as e:
        st.error("Terjadi kesalahan saat mengonversi: " + str(e))
