"""Document parsing and chunking for vector storage"""
from typing import List
import nomic
from llama_cloud_services import LlamaParse
from llama_index.core import SimpleDirectoryReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document as LangchainDocument

from src.config import LLAMA_CLOUD_API_KEY, NOMIC_API_KEY, CHUNK_SIZE, CHUNK_OVERLAP

# Initialize LlamaParse for PDF extraction
llamaparse = LlamaParse(
    api_key=LLAMA_CLOUD_API_KEY,
    result_type="markdown"  # Better structure preservation
)

def parse_documents(files: List[str]) -> List:
    """Parse PDFs using LlamaParse"""
    file_extractor = {".pdf": llamaparse}
    documents = SimpleDirectoryReader(input_files=files, file_extractor=file_extractor).load_data()
    return documents

def process_documents(files: List[str]) -> str:
    """Parse PDFs, convert to LangChain format, and split into chunks"""
    # Parse PDFs
    documents = parse_documents(files)

    # Convert to LangChain document format
    langchain_docs = [
        LangchainDocument(
            page_content=doc.text,
            metadata=doc.metadata
        ) for doc in documents
    ]

    # Split into chunks with overlap for context preservation
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    splits = text_splitter.split_documents(langchain_docs)

    # TODO: Store splits in vector database
    # Example: atlas_store.add_documents(splits)

    return f"Processed {len(splits)} document chunks"