"""Gradio web interface for RAT demo"""
import gradio as gr
import time
from datetime import datetime

from src.document_processing import process_documents
from src.reasoning import rat, simple_rag

def create_demo():
    """Create Gradio UI with RAG vs RAT comparison"""

    def clear_func():
        """Reset UI fields"""
        return "", "", ""

    def process_query(question):
        """Process query through RAG and RAT, compare results"""
        # Run Simple RAG
        rag_start_time = time.time()
        rag_answer = simple_rag(question)
        rag_processing_time = time.time() - rag_start_time
        print(f"RAG Processing Time: {rag_processing_time:.2f} seconds")

        # Run RAT (draft + iterative retrieval/revision)
        rat_start_time = time.time()
        _, rat_answer = rat(question)
        rat_processing_time = time.time() - rat_start_time
        print(f"RAT Processing Time: {rat_processing_time:.2f} seconds")

        # Format results with timing
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

    # Build Gradio UI
    demo = gr.Blocks(title="RAT with Documents")

    with demo:
        gr.Markdown("# Retrieval-Augmented Tool with Documents")

        # Document upload popup (hidden by default)
        with gr.Column(visible=False) as upload_popup:
            gr.Markdown("### Upload Documents")
            file_output = gr.File(label="Select Files", file_count="multiple")
            confirm_upload_btn = gr.Button("Upload")
            cancel_upload_btn = gr.Button("Cancel")
            upload_status = gr.Textbox(label="Processing Status")

        # Main controls
        with gr.Row():
            upload_btn = gr.Button("📁 Upload Documents")
            submit_btn = gr.Button("Submit Query")
            clear_btn = gr.Button("Clear All")

        # Question input
        instruction_box = gr.Textbox(label="Your Question", placeholder="Enter your question here...", lines=3)

        # Side-by-side comparison output
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### RAG Response")
                rag_box = gr.Markdown(label="", elem_id="rag-output")

            with gr.Column(scale=1):
                gr.Markdown("### RAT Response")
                rat_box = gr.Markdown(label="", elem_id="rat-output")

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

    # Custom CSS
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