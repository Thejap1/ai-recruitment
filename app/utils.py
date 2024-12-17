import json

# Load questions from data.json
def load_questions(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data["questions"]

# Updated calculate_score function
def calculate_score(form_data, questions):
    score = 0
    total_questions = len(questions)

    for idx, question in enumerate(questions):
        selected_answer = form_data.get(f'questions-{idx}-answer')
        correct_answer = question["correct_answer"]

        if selected_answer == correct_answer:
            score += 1

    # Calculate the percentage score
    percentage_score = (score / total_questions) * 100
    return percentage_score

