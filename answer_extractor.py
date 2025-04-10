import re
import random

def simple_answer_extraction(context, question):
    """
    Simple rule-based answer extraction from context.
    
    Args:
        context (str): The text passage
        question (str): The question to answer
        
    Returns:
        str: The extracted answer
    """
    # For fill-in-the-blank, we already have the answers from generation
    if "________" in question:
        return "Cannot determine from the context."
    
    # For true/false, answers should already be provided
    if question.lower().startswith(("true or false", "is the following", "indicate whether")):
        return random.choice(["True", "False"])
    
    # For other questions, extract relevant sentences from context
    question_lower = question.lower()
    question_words = set(re.findall(r'\b\w+\b', question_lower))
    
    # Remove common question words and stop words to focus on content words
    stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                 'what', 'where', 'when', 'why', 'how', 'who', 'which', 'in', 'on', 
                 'at', 'to', 'for', 'with', 'by', 'about', 'this', 'that', 'these', 
                 'those', 'from', 'as', 'of', 'does', 'do', 'did', 'can', 'could', 
                 'will', 'would', 'should', 'shall', 'may', 'might', 'must'}
    
    content_words = question_words - stop_words
    
    # Split context into sentences and score them based on question word overlap
    sentences = re.split(r'(?<=[.!?])\s+', context)
    
    if not sentences:
        return "Based on the passage, this information is not explicitly stated."
    
    sentence_scores = []
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        score = sum(1 for word in content_words if word in sentence_lower)
        
        # Boost score for first few sentences as they often contain key information
        if i < 2:
            score += 1
            
        sentence_scores.append((score, i, sentence))
    
    # Sort sentences by score, highest first
    sentence_scores.sort(reverse=True)
    
    # Return the highest scoring sentence as the answer
    if sentence_scores and sentence_scores[0][0] > 0:
        return sentence_scores[0][2]
    
    # Fallback answer if no good match is found
    return "Based on the passage, this information is not explicitly stated."

def extract_answers(context, questions_by_type):
    """
    Extract answers for each question using the context.
    
    Args:
        context (dict or str): The processed text or raw text
        questions_by_type (dict): Questions organized by type
        
    Returns:
        dict: Questions with answers
    """
    # Get the text from context
    if isinstance(context, dict):
        text = context["text"]
    else:
        text = context
    
    # Process each question type
    questions_with_answers = {}
    
    for q_type, questions in questions_by_type.items():
        questions_with_answers[q_type] = []
        
        for q in questions:
            # For some question types, we already have the answer
            if q_type in ["fill-in-the-blank", "true-false"]:
                # Just use the existing answer
                questions_with_answers[q_type].append(q)
                continue
            
            # For other question types, extract or refine the answer
            question_text = q["question"]
            
            # If the question already has a reasonable answer, use it
            if "answer" in q and len(q["answer"]) > 5:
                # Use the existing answer
                questions_with_answers[q_type].append(q)
            else:
                # Extract a new answer
                answer = simple_answer_extraction(text, question_text)
                questions_with_answers[q_type].append({
                    "question": question_text,
                    "answer": answer
                })
    
    return questions_with_answers
