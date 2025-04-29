"""
Document parsing, processing and vector storage functions
"""
from typing import List
import nomic
from llama_cloud_services import LlamaParse
from llama_index.core import SimpleDirectoryReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document as LangchainDocument

from src.config import LLAMA_CLOUD_API_KEY, NOMIC_API_KEY, CHUNK_SIZE, CHUNK_OVERLAP

# Initialize LlamaParse for document extraction
llamaparse = LlamaParse(
    api_key=LLAMA_CLOUD_API_KEY,
    result_type="markdown"
)

def parse_documents(files: List[str]) -> List:
    """Parse uploaded documents using LlamaParse"""
    file_extractor = {".pdf": llamaparse}
    documents = SimpleDirectoryReader(input_files=files, file_extractor=file_extractor).load_data()
    return documents

def process_documents(files: List[str]) -> str:
    """Process and split documents for storage"""
    # Parse documents
    documents = parse_documents(files)
        
    langchain_docs = [
        LangchainDocument(
            page_content=doc.text,
            metadata=doc.metadata
        ) for doc in documents
    ]
    
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP
    )
    splits = text_splitter.split_documents(langchain_docs)
    
    # In a complete implementation, you would store these in your vector database
    # or initialize your Atlas dataset with these documents
    
    return f"Processed {len(splits)} document chunks"