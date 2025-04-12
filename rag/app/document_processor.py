from typing import List, Dict, Optional
from pathlib import Path
import nltk
from nltk.tokenize import sent_tokenize
from llamaparse import LlamaParse
import hashlib


class DocumentProcessor:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.parser = LlamaParse()

    def process_text(self, text: str, metadata: Optional[Dict] = None) -> List[Dict]:
        """Split text into chunks with metadata"""
        chunks = self._chunk_text(text)

        base_metadata = metadata or {}
        text_hash = hashlib.md5(text.encode()).hexdigest()

        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update(
                {
                    "chunk_id": f"{text_hash}_{i}",
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "text": chunk,
                }
            )
            processed_chunks.append(chunk_metadata)

        return processed_chunks

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into semantically meaningful chunks"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)

            if current_length + sentence_length > self.chunk_size:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    async def process_file(
        self, file_path: str, metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Process different file types and extract text with metadata"""
        file_path = Path(file_path)
        base_metadata = {
            "source": str(file_path),
            "file_type": file_path.suffix.lower()[1:],
            "filename": file_path.name,
        }

        if metadata:
            base_metadata.update(metadata)

        # Extract text based on file type
        if file_path.suffix.lower() in [".txt", ".md"]:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            # Use LlamaParse for other document types
            text = await self.parser.parse_file(str(file_path))

        return self.process_text(text, base_metadata)
