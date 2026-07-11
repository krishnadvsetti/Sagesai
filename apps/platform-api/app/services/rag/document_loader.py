from pathlib import Path

from pypdf import PdfReader


class DocumentLoader:
    @staticmethod
    def load(file_path: Path) -> str:
        suffix = file_path.suffix.lower()

        if suffix == ".pdf":
            reader = PdfReader(file_path)
            return "\n".join(
                page.extract_text() or "" for page in reader.pages
            ).strip()

        if suffix == ".txt":
            return file_path.read_text(encoding="utf-8")

        raise ValueError(f"Unsupported file type: {suffix}")