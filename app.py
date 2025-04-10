import streamlit as st
import pandas as pd
import time

from text_processor import preprocess_text
from question_generator import generate_questions
from answer_extractor import extract_answers
from question_classifier import classify_questions
from export_util import export_to_csv

# Set page config
st.set_page_config(
    page_title="AI Comprehension Question Generator",
    page_icon="📚",
    layout="wide"
)

# Application title and description
st.title("AI Comprehension Question Generator")
st.markdown("""
This application helps you generate different types of comprehension questions from any text.
Simply paste your text below and click 'Generate Questions' to get started!
""")

# Text input area
text_input = st.text_area(
    "Paste your text passage here:",
    height=200,
    placeholder="Enter a paragraph or a passage here to generate questions..."
)

# Sidebar for controls and options
with st.sidebar:
    st.header("Question Generation Options")
    
    # Question type selection
    st.subheader("Question Types")
    fill_blanks = st.checkbox("Fill in the blanks", value=True)
    true_false = st.checkbox("True/False", value=True)
    short_answer = st.checkbox("Short Answer", value=True)
    long_answer = st.checkbox("Long Answer", value=True)
    
    # Number of questions slider
    num_questions = st.slider(
        "Number of questions per type",
        min_value=1,
        max_value=10,
        value=3
    )
    
    # Advanced options (collapsible)
    with st.expander("Advanced Options"):
        preprocessing_level = st.radio(
            "Text Preprocessing Level",
            options=["Basic"],
            index=0
        )

# Generate questions button
if st.button("Generate Questions"):
    if not text_input or len(text_input.strip()) < 50:
        st.error("Please enter a substantial text passage (at least 50 characters) to generate meaningful questions.")
    else:
        # Process the text and generate questions with a progress bar
        with st.spinner("Processing text and generating questions..."):
            # Progress bar for visual feedback
            progress_bar = st.progress(0)
            
            # Step 1: Preprocess text
            progress_bar.progress(10)
            processed_text = preprocess_text(text_input, level=preprocessing_level.lower())
            
            # Step 2: Generate questions
            progress_bar.progress(30)
            selected_types = []
            if fill_blanks:
                selected_types.append("fill-in-the-blank")
            if true_false:
                selected_types.append("true-false")
            if short_answer:
                selected_types.append("short-answer")
            if long_answer:
                selected_types.append("long-answer")
            
            raw_questions = generate_questions(
                processed_text, 
                num_questions=num_questions,
                question_types=selected_types
            )
            
            # Step 3: Extract answers
            progress_bar.progress(60)
            questions_with_answers = extract_answers(processed_text, raw_questions)
            
            # Step 4: Classify questions
            progress_bar.progress(80)
            classified_questions = classify_questions(questions_with_answers)
            
            # Complete progress
            progress_bar.progress(100)
            time.sleep(0.5)  # Small delay to show completed progress
            progress_bar.empty()  # Remove progress bar
        
        st.success("Successfully generated questions!")
        
        # Display questions by type
        tab_titles = []
        if fill_blanks and "fill-in-the-blank" in classified_questions:
            tab_titles.append("Fill in the Blanks")
        if true_false and "true-false" in classified_questions:
            tab_titles.append("True/False")
        if short_answer and "short-answer" in classified_questions:
            tab_titles.append("Short Answer")
        if long_answer and "long-answer" in classified_questions:
            tab_titles.append("Long Answer")
        
        tabs = st.tabs(tab_titles)
        
        tab_index = 0
        all_questions = []  # For export functionality
        
        # Fill in the blanks questions
        if fill_blanks and "fill-in-the-blank" in classified_questions and tab_index < len(tabs):
            with tabs[tab_index]:
                st.subheader("Fill in the Blanks Questions")
                for i, qa_pair in enumerate(classified_questions["fill-in-the-blank"]):
                    with st.expander(f"Question {i+1}"):
                        st.write(qa_pair["question"])
                        st.text_input("Your Answer:", key=f"fib_{i}", placeholder="Write your answer here")
                        st.info(f"Answer: {qa_pair['answer']}")
                    all_questions.append({
                        "Type": "Fill in the Blanks",
                        "Question": qa_pair["question"],
                        "Answer": qa_pair["answer"]
                    })
            tab_index += 1
        
        # True/False questions
        if true_false and "true-false" in classified_questions and tab_index < len(tabs):
            with tabs[tab_index]:
                st.subheader("True/False Questions")
                for i, qa_pair in enumerate(classified_questions["true-false"]):
                    with st.expander(f"Question {i+1}"):
                        st.write(qa_pair["question"])
                        st.radio("Your Answer:", ["True", "False"], key=f"tf_{i}")
                        st.info(f"Answer: {qa_pair['answer']}")
                    all_questions.append({
                        "Type": "True/False",
                        "Question": qa_pair["question"],
                        "Answer": qa_pair["answer"]
                    })
            tab_index += 1
        
        # Short answer questions
        if short_answer and "short-answer" in classified_questions and tab_index < len(tabs):
            with tabs[tab_index]:
                st.subheader("Short Answer Questions")
                for i, qa_pair in enumerate(classified_questions["short-answer"]):
                    with st.expander(f"Question {i+1}"):
                        st.write(qa_pair["question"])
                        st.text_input("Your Answer:", key=f"sa_{i}", placeholder="Write your answer here")
                        st.info(f"Answer: {qa_pair['answer']}")
                    all_questions.append({
                        "Type": "Short Answer",
                        "Question": qa_pair["question"],
                        "Answer": qa_pair["answer"]
                    })
            tab_index += 1
        
        # Long answer questions
        if long_answer and "long-answer" in classified_questions and tab_index < len(tabs):
            with tabs[tab_index]:
                st.subheader("Long Answer Questions")
                for i, qa_pair in enumerate(classified_questions["long-answer"]):
                    with st.expander(f"Question {i+1}"):
                        st.write(qa_pair["question"])
                        st.text_area("Your Answer:", key=f"la_{i}", placeholder="Write your answer here", height=100)
                        st.info(f"Answer: {qa_pair['answer']}")
                    all_questions.append({
                        "Type": "Long Answer",
                        "Question": qa_pair["question"],
                        "Answer": qa_pair["answer"]
                    })
        
        # Create a DataFrame for export functionality
        if all_questions:
            questions_df = pd.DataFrame(all_questions)
            csv_data = export_to_csv(questions_df)
            
            st.download_button(
                label="Download Questions & Answers as CSV",
                data=csv_data,
                file_name="comprehension_questions.csv",
                mime="text/csv",
            )
