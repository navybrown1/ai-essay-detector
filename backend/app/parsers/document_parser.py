import tempfile
import os


def parse_txt(content: bytes) -> str:
    return content.decode("utf-8", errors="replace")


def parse_docx(content: bytes) -> str:
    from docx import Document
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        doc = Document(tmp_path)
        return "\n".join(p.text for p in doc.paragraphs)
    finally:
        os.unlink(tmp_path)


def parse_pdf(content: bytes) -> str:
    import pdfplumber
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        text_parts = []
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n".join(text_parts)
    finally:
        os.unlink(tmp_path)


def parse_file(filename: str, content: bytes) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext == "txt":
        return parse_txt(content)
    elif ext == "docx":
        return parse_docx(content)
    elif ext == "pdf":
        return parse_pdf(content)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
