"""
Utilities for text processing, chunking, and token counting
"""
import tiktoken
from typing import List

def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def chunk_text_by_sentence(text: str, chunk_size: int = 2048) -> str:
    """Chunk the text into sentences with less than chunk_size tokens."""
    sentences = text.split('. ')
    chunked_text = []
    curr_chunk = []
    for sentence in sentences:
        if num_tokens_from_string(". ".join(curr_chunk)) + num_tokens_from_string(sentence) + 2 <= chunk_size:
            curr_chunk.append(sentence)
        else:
            chunked_text.append(". ".join(curr_chunk))
            curr_chunk = [sentence]
    if curr_chunk:
        chunked_text.append(". ".join(curr_chunk))
    return chunked_text[0]

def chunk_text_front(text: str, chunk_size: int = 2048) -> str:
    '''Get the first `chunk_size` tokens of text'''
    tokens = num_tokens_from_string(text)
    if tokens < chunk_size:
        return text
    else:
        ratio = float(chunk_size) / tokens
        char_num = int(len(text) * ratio)
        return text[:char_num]

def chunk_texts(text: str, chunk_size: int = 2048) -> List[str]:
    '''Chunk the text into n parts, return a list of text'''
    tokens = num_tokens_from_string(text)
    if tokens < chunk_size:
        return [text]
    else:
        texts = []
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