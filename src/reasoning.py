"""
RAT and RAG reasoning implementations
"""
import time
from datetime import datetime
from multiprocessing import Process, Queue
from langchain.schema import HumanMessage
from langchain_community.chat_models import ChatOllama
from IPython.display import display, HTML

from src.config import DEFAULT_LLM, DEFAULT_TEMPERATURE
from src.retrieval import retrieve_context
from src.utils.text_utils import chunk_text_front
from src.utils.diff_utils import generate_diff_html

# Initialize LLM
llm = DEFAULT_LLM
newline_char = '\n'


def run_with_timeout(func, timeout, *args, **kwargs):
    """Run function with timeout using multiprocessing"""
    q = Queue()
    p = Process(target=func, args=(q, *args), kwargs=kwargs)
    p.start()
    p.join(timeout)
    
    if p.is_alive():
        print(f"{datetime.now()} [INFO] Function {str(func)} running timeout ({timeout}s), terminating...")
        p.terminate() 
        p.join()  
        result = None  
    else:
        print(f"{datetime.now()} [INFO] Function {str(func)} executed successfully.")
        result = q.get() 
    return result

def get_draft(question):
    """Generate initial draft answer"""
    draft_prompt = '''
IMPORTANT:
Try to answer this question/instruction with step-by-step thoughts and make the answer more structural.
Use `\n\n` to split the answer into several paragraphs.
Just respond to the instruction directly. DO NOT add additional explanations or introducement in the answer unless you are asked to.
'''
    chat = ChatOllama(model=llm, temperature=DEFAULT_TEMPERATURE)
    messages = [HumanMessage(content=f"{question}" + draft_prompt)]
    return chat.invoke(messages).content

def split_draft(draft, split_char='\n\n'):
    """Split a draft answer into paragraphs"""
    paragraphs = draft.split(split_char)
    draft_paragraphs = [para for para in paragraphs if len(para)>5]
    return draft_paragraphs

def split_draft_openai(question, answer, NUM_PARAGRAPHS=4):
    """Split answer into paragraphs using LLM"""
    split_prompt = f'''
Split the answer of the question into multiple paragraphs with each paragraph containing a complete thought.
The answer should be splited into less than {NUM_PARAGRAPHS} paragraphs.
Use ## as splitting char to seperate the paragraphs.
So you should output the answer with ## to split the paragraphs.
**IMPORTANT**
Just output the query directly. DO NOT add additional explanations or introducement in the answer unless you are asked to.
'''
    chat = ChatOllama(model=llm, temperature=DEFAULT_TEMPERATURE)
    messages = [
        HumanMessage(content=f"##Question: {question}\n\n##Response: {answer}\n\n##Instruction: {split_prompt}")
    ]
    splited_answer = chat.invoke(messages).content
    split_draft_paragraphs = split_draft(splited_answer, split_char='##')
    return split_draft_paragraphs

def get_query(question, answer):
    """Generate search query from question and answer"""
    query_prompt = '''
I want to verify the content correctness of the given question, especially the last sentences.
Please summarize the content with the corresponding question.
This summarization will be used as a query to search with Bing search engine.
The query should be short but need to be specific to promise Bing can find related knowledge or pages.
You can also use search syntax to make the query short and clear enough for the search engine to find relevant language data.
Try to make the query as relevant as possible to the last few sentences in the content.
**IMPORTANT**
Just output the query directly. DO NOT add additional explanations or introducement in the answer unless you are asked to.
'''
    chat = ChatOllama(model=llm, temperature=DEFAULT_TEMPERATURE)
    messages = [
        HumanMessage(content=f"##Question: {question}\n\n##Content: {answer}\n\n##Instruction: {query_prompt}")
    ]
    return chat.invoke(messages).content

def get_content(query):
    """Retrieve context from Nomic Atlas"""
    retrieved_results = retrieve_context(query)
    
    # Check if we have results and if they're dictionaries
    if not retrieved_results:
        return []
        
    trunked_texts = []
    for result in retrieved_results:
        if isinstance(result, dict):
            if 'text' in result:
                text = result['text']
            elif 'content' in result:
                text = result['content']
            elif 'page_content' in result:
                text = result['page_content']
            else:
                text = str(result)
        else:
            text = str(result)
            
        if text:
            trunked_texts.append(chunk_text_front(text, 1500).replace('\n', " "))
            
    return trunked_texts

def get_revise_answer(question, answer, content):
    """Revise answer based on retrieved content"""
    revise_prompt = '''
I want to revise the answer according to retrieved related text of the question in WIKI pages.
You need to check whether the answer is correct.
If you find some errors in the answer, revise the answer to make it better.
If you find some necessary details are ignored, add it to make the answer more plausible according to the related text.
If you find the answer is right and do not need to add more details, just output the original answer directly.
**IMPORTANT**
Try to keep the structure (multiple paragraphs with its subtitles) in the revised answer and make it more structual for understanding.
Add more details from retrieved text to the answer.
Split the paragraphs with \n\n characters.
Just output the revised answer directly. DO NOT add additional explanations or annoucement in the revised answer unless you are asked to.
'''
    chat = ChatOllama(model=llm, temperature=DEFAULT_TEMPERATURE)
    messages = [
        HumanMessage(content=f"##Existing Text in Wiki Web: {content}\n\n##Question: {question}\n\n##Answer: {answer}\n\n##Instruction: {revise_prompt}")
    ]
    return chat.invoke(messages).content

def get_reflect_answer(question, answer):
    """Add formatting and structure to the final answer"""
    reflect_prompt = '''
Give a title for the answer of the question.
And add a subtitle to each paragraph in the answer and output the final answer using markdown format.
When appropriate, organize information using bullet points or numbered lists.
This will make the answer to this question look more structured for better understanding.

**IMPORTANT**
- Maintain the structure (multiple paragraphs with subtitles) in the response
- Use bullet points or numbered lists for listing items, steps, or features
- Format key concepts with bold or italic text for emphasis
- Use code blocks when presenting technical content, formulas, or examples
- Split the paragraphs with \n\n characters

Just output the revised answer directly. DO NOT add additional explanations or announcements in the revised answer unless you are asked to.
'''
    chat = ChatOllama(model=llm, temperature=DEFAULT_TEMPERATURE)
    messages = [
        HumanMessage(content=f"##Question:\n{question}\n\n##Answer:\n{answer}\n\n##Instruction:\n{reflect_prompt}")
    ]
    return chat.invoke(messages).content

# Wrapper functions for multiprocessing
def get_query_wrapper(q, question, answer):
    result = get_query(question, answer)
    q.put(result)

def get_content_wrapper(q, query):
    result = get_content(query)
    q.put(result)

def get_revise_answer_wrapper(q, question, answer, content):
    result = get_revise_answer(question, answer, content)
    q.put(result)

def get_reflect_answer_wrapper(q, question, answer):
    result = get_reflect_answer(question, answer)
    q.put(result)

def rat(question):
    
    """Full RAT reasoning implementation"""
    print(f"{datetime.now()} [INFO] Generating draft...")
    draft = get_draft(question)
    print(f"{datetime.now()} [INFO] Return draft.")

    print(f"{datetime.now()} [INFO] Processing draft ...")
    draft_paragraphs = split_draft_openai(question, draft)
    print(f"{datetime.now()} [INFO] Draft is splitted into {len(draft_paragraphs)} sections.")
    
    answer = ""
    for i, p in enumerate(draft_paragraphs):
        print(f"{datetime.now()} [INFO] Revising {i+1}/{len(draft_paragraphs)} sections ...")
        answer = answer + '\n\n' + p

        # Generate query
        print(f"{datetime.now()} [INFO] Generating query ...")
        res = run_with_timeout(get_query_wrapper, 300, question, answer)
        if not res:
            print(f"{datetime.now()} [INFO] Generating query timeout, skipping...")
            continue
        else:
            query = res
            print(f">>> {i}/{len(draft_paragraphs)} Query: {query.replace(newline_char, ' ')}")
        # Retrieve content
        print(f"{datetime.now()} [INFO] Retrieving documents ...")
        res = run_with_timeout(get_content_wrapper, 300, query)
        if not res:
            print(f"{datetime.now()} [INFO] Retrieving documents timeout, skipping ...")
            continue
        else:
            content = res

        # Revise answer with retrieved content
        LIMIT = 2
        for j, c in enumerate(content):
            if j >= LIMIT:  # limit the number of documents
                break
            print(f"{datetime.now()} [INFO] Revising answers with retrieved documents...[{j}/{min(len(content),LIMIT)}]")
            res = run_with_timeout(get_revise_answer_wrapper, 300, question, answer, c)
            if not res:
                print(f"{datetime.now()} [INFO] Revising answers timeout, skipping ...")
                continue
            else:
                diff_html = generate_diff_html(answer, res)
                display(HTML(diff_html))
                answer = res
            print(f"{datetime.now()} [INFO] Answer revised [{j}/{min(len(content),LIMIT)}]")

    # Final reflection and formatting
    res = run_with_timeout(get_reflect_answer_wrapper, 300, question, answer)
    if not res:
        print(f"{datetime.now()} [INFO] Reflecting answers timeout, skipping next steps...")
    else:
        answer = res
    
    return draft, answer

def simple_rag(question):
    """Simple RAG implementation with single retrieval step"""
    context = retrieve_context(question, k=5)
    context_str = "\n\n".join([chunk_text_front(c.get('text', ''), 1500) for c in context])
    
    prompt = f"""Answer the question based on the following context:
    
    {context_str}
    
    Question: {question}
    """
    
    chat = ChatOllama(model=llm, temperature=DEFAULT_TEMPERATURE)
    messages = [HumanMessage(content=prompt)]
    answer = chat.invoke(messages).content
    
    formatted_answer = get_reflect_answer(question, answer)
    return formatted_answer