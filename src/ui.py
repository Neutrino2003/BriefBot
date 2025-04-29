"""
Gradio interface for RAT demo
"""
import gradio as gr
import time
from datetime import datetime

from src.document_processing import process_documents
from src.reasoning import rat, simple_rag

def create_demo():
    """Create and configure the Gradio demo interface"""
    
    # Clear function for resetting the UI
    def clear_func():
        return "", "", ""

    # Function to process query and compare RAG and RAT
    def process_query(question):
        rag_start_time = time.time()
        
        rag_answer = simple_rag(question)
        
        rag_end_time = time.time()
        rag_processing_time = rag_end_time - rag_start_time
        print(f"RAG Processing Time: {rag_processing_time:.2f} seconds")
        
        rat_start_time = time.time()
        
        _, rat_answer = rat(question)
        
        rat_end_time = time.time()
        rat_processing_time = rat_end_time - rat_start_time
        print(f"RAT Processing Time: {rat_processing_time:.2f} seconds")
        
        total_processing_time = rag_processing_time + rat_processing_time
        print(f"Total Processing Time: {total_processing_time:.2f} seconds")
        
        formatted_rag_answer = f"\n{rag_answer}\n\n**Processing Time:** `{rag_processing_time:.2f} seconds`"
        formatted_rat_answer = f"\n{rat_answer}\n\n**Processing Time:** `{rat_processing_time:.2f} seconds`"
        formatted_total_time = f"### Total Processing Time\n\n`{total_processing_time:.2f} seconds`"
        
        return {
            rag_box: formatted_rag_answer,
            rat_box: formatted_rat_answer,
            processing_time_box: formatted_total_time
        }

    # Create the Gradio interface
    demo = gr.Blocks(title="RAT with Documents")
    
    with demo:
        gr.Markdown("# Retrieval-Augmented Tool with Documents")

        # Hidden upload section (simulating a popup)
        with gr.Column(visible=False) as upload_popup:
            gr.Markdown("### Upload Documents")
            file_output = gr.File(label="Select Files", file_count="multiple")
            confirm_upload_btn = gr.Button("Upload")
            cancel_upload_btn = gr.Button("Cancel")
            upload_status = gr.Textbox(label="Processing Status")

        # Main Interface
        with gr.Row():
            upload_btn = gr.Button("📁 Upload Documents")
            submit_btn = gr.Button("Submit Query")
            clear_btn = gr.Button("Clear All")

        # Input section
        instruction_box = gr.Textbox(label="Your Question", placeholder="Enter your question here...", lines=3)

        # Output comparison section
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### RAG Response")
                rag_box = gr.Markdown(label="", elem_id="rag-output")
                
            with gr.Column(scale=1):
                gr.Markdown("### RAT Response")
                rat_box = gr.Markdown(label="", elem_id="rat-output")
        
        # Hidden initial answer
        chatgpt_box = gr.Textbox(visible=False)
        processing_time_box = gr.Markdown(label="Processing Time", elem_id="processing-time-output")

        # Event handlers
        upload_btn.click(lambda: gr.update(visible=True), outputs=upload_popup)

        confirm_upload_btn.click(
            fn=process_documents,
            inputs=[file_output],
            outputs=[upload_status],
            show_progress=True
        ).then(lambda: gr.update(visible=False), outputs=upload_popup)

        cancel_upload_btn.click(lambda: gr.update(visible=False), outputs=upload_popup)

        submit_btn.click(
            fn=process_query,
            inputs=[instruction_box],
            outputs=[rag_box, rat_box, processing_time_box]
        )
        
        clear_btn.click(
            fn=clear_func,
            inputs=[],
            outputs=[instruction_box, rag_box, rat_box]
        )

    # Add custom CSS for better visualization
    demo.css += """
    .thought-process {
        white-space: pre-wrap;
        word-wrap: break-word;
        background: #f8f8f8;
        border-radius: 8px;
        padding: 15px;
        margin-top: 10px;
        max-height: 400px;
        overflow-y: auto;
    }
    """
    
    return demo