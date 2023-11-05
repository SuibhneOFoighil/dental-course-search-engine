"""
Generates a quiz with questions and answers from the intro dict and the chat history.
"""

import re
import json

def parse_text(text):
    """
    Parse a text into a dictionary with theme headers and paragraph bodies.

    Arguments:
    text -- String containing themes headers and paragraphs separated by '\\n\\n'

    Returns: 
    dictionary with theme headers as keys and paragraph bodies as values
    """
    
    paragraphs = re.split(r'\n\n', text)

    themes = []
    paragraphs_by_theme = {}
    for i in range(0, len(paragraphs) - 1, 2):
        theme = paragraphs[i] 
        theme = theme.split('**')[1].strip()
        theme = theme.replace(':', '')
        themes.append(theme)

        paragraph = paragraphs[i+1]
        paragraphs_by_theme[theme] = paragraph

    return paragraphs_by_theme


def make_quiz(intro: dict, chat_history: list) -> list[dict]:
    # Get the themes from the intro
    themes = parse_text(intro['themes'])

    # Extract question / answer pairs from the chat history
    qa_pairs = []
    for i, message in enumerate(chat_history):
        if message.role == 'user':
            question = message.content
            answer = chat_history[i + 1].content
            qa_pairs.append({'question': question, 'answer': answer})
        else:
            continue

    # Generate the quiz
    quiz = []
    n_questions_per_item = 3

    # Generate questions for each theme
    for theme, text in themes.items():
        data = {}
        # generate questions for the theme
        questions = []
        for i in range(n_questions_per_item):
            input_data = f"""
            {theme}
            {text}
            """
            generated_question = generate_question(input_data)

        data['questions'] = questions
        quiz.append(data)

    # Generate questions for each question / answer pair
    for qa_pair in qa_pairs:
        data = {}
        # generate questions for the theme
        questions = []
        for i in range(n_questions_per_item):
            input_data = f"""
            {qa_pair['question']}
            {qa_pair['answer']}
            """
            generated_question = generate_question(input_data)

        data['questions'] = questions
        quiz.append(data)

    #Generate answers for each question
    for question in quiz:
        question['answer'] = generate_answer(question['question'])

    return quiz
    

def test():
    #load in the summary json
    with open('summary.json', 'r') as f:
        summary = json.load(f)
    
    themes = parse_text(summary['themes'])

    print(themes)

def generate_question(input_data: str) -> str:
    """
    Generates a question from the input data.

    Arguments:
    input_data -- String containing the input data for the question generation.

    Returns:
    String containing the generated question.
    """
    return "What is the question?"

def generate_answer(question: str) -> str:
    """
    Generates an answer from the input question.

    Arguments:
    question -- String containing the question.

    Returns:
    String containing the generated answer.
    """
    return "This is the answer."

if __name__ == "__main__":
    test()
