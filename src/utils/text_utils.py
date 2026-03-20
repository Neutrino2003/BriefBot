"""Text processing, chunking, and token counting utilities"""
import tiktoken
from typing import List

def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Count tokens in text using tiktoken"""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def chunk_text_by_sentence(text: str, chunk_size: int = 2048) -> str:
    """Split text at sentence boundaries, return first chunk under token limit"""
    sentences = text.split('. ')
    chunked_text = []
    curr_chunk = []
    for sentence in sentences:
        # Check if adding sentence exceeds chunk_size
        if num_tokens_from_string(". ".join(curr_chunk)) + num_tokens_from_string(sentence) + 2 <= chunk_size:
            curr_chunk.append(sentence)
        else:
            chunked_text.append(". ".join(curr_chunk))
            curr_chunk = [sentence]
    if curr_chunk:
        chunked_text.append(". ".join(curr_chunk))
    return chunked_text[0]

def chunk_text_front(text: str, chunk_size: int = 2048) -> str:
    """Truncate text to first `chunk_size` tokens"""
    tokens = num_tokens_from_string(text)
    if tokens < chunk_size:
        return text
    else:
        # Use character ratio for fast approximation
        ratio = float(chunk_size) / tokens
        char_num = int(len(text) * ratio)
        return text[:char_num]

def chunk_texts(text: str, chunk_size: int = 2048) -> List[str]:
    """Split text into n balanced chunks under token limit"""
    tokens = num_tokens_from_string(text)
    if tokens < chunk_size:
        return [text]
    else:
        # Calculate number of chunks needed
        n = int(tokens/chunk_size) + 1
        part_length = len(text) // n
        extra = len(text) % n
        parts = []
        start = 0

        for i in range(n):
            end = start + part_length + (1 if i < extra else 0)
            parts.append(text[start:end])
            start = end
        return parts
