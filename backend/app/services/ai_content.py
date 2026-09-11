"""
AI-generated learning content: quiz questions, answer explanations, and
short practice/explanation material for a topic, scaled to a difficulty
level.

Uses the OpenAI API when OPENAI_API_KEY is configured; otherwise falls back
to a deterministic offline question generator so the platform works locally
without an API key.
"""

import json
import random
from typing import List

from app.config import settings


# ---------------------------------------------------------------------------
# Optional OpenAI client
# ---------------------------------------------------------------------------

_client = None

if settings.openai_api_key:
    from openai import OpenAI

    _client = OpenAI(api_key=settings.openai_api_key)


# ---------------------------------------------------------------------------
# OpenAI response format instructions
# ---------------------------------------------------------------------------

QUESTION_SCHEMA_INSTRUCTIONS = """
Return ONLY a JSON array (no prose, no markdown fences).

Each element must be an object with exactly these keys:

  "prompt": string,
  "option_a": string,
  "option_b": string,
  "option_c": string,
  "option_d": string,
  "correct_option": one of "A" | "B" | "C" | "D",
  "explanation": string

The explanation must contain 2-3 sentences explaining why the correct
answer is right, written for a student at the target difficulty level.
"""


# ---------------------------------------------------------------------------
# Quiz generation
# ---------------------------------------------------------------------------

def generate_quiz_questions(
    topic_title: str,
    topic_summary: str,
    difficulty: str,
    num_questions: int = 5,
) -> List[dict]:
    """
    Generate multiple-choice quiz questions.

    If an OpenAI API key is configured, OpenAI generates the questions.

    If no API key is configured, the application uses the built-in offline
    question bank instead.
    """

    # -----------------------------------------------------------------------
    # OpenAI generation
    # -----------------------------------------------------------------------

    if _client:
        prompt = (
            f"Create {num_questions} multiple-choice quiz questions for the "
            f"topic '{topic_title}'. "
            f"Topic summary: {topic_summary or 'N/A'}. "
            f"Target difficulty: {difficulty}. "
            f"{QUESTION_SCHEMA_INSTRUCTIONS}"
        )

        response = _client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert instructional designer who writes "
                        "precise, unambiguous educational quiz questions."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.7,
        )

        raw = response.choices[0].message.content.strip()

        # Remove markdown JSON fences if the model accidentally returns them.
        raw = (
            raw
            .removeprefix("```json")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )

        questions = json.loads(raw)

        return questions[:num_questions]

    # -----------------------------------------------------------------------
    # Offline fallback
    # -----------------------------------------------------------------------

    return _template_questions(
        topic_title=topic_title,
        difficulty=difficulty,
        num_questions=num_questions,
    )


# ---------------------------------------------------------------------------
# Explanation generation
# ---------------------------------------------------------------------------

def generate_explanation(
    question_prompt: str,
    correct_answer_text: str,
    difficulty: str,
) -> str:
    """
    Generate an explanation for a question.
    """

    if _client:
        response = _client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Explain concisely for a student in 2-3 sentences."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question: {question_prompt}\n"
                        f"Correct answer: {correct_answer_text}\n"
                        f"Student level: {difficulty}. "
                        f"Explain why this answer is correct."
                    ),
                },
            ],
            temperature=0.5,
        )

        return response.choices[0].message.content.strip()

    return (
        f"The correct answer is '{correct_answer_text}'. "
        f"At the {difficulty} level, focus on why this option directly "
        f"satisfies what the question asks, and review the related topic "
        f"material if this wasn't clear."
    )


# ---------------------------------------------------------------------------
# Practice material generation
# ---------------------------------------------------------------------------

def generate_practice_material(
    topic_title: str,
    topic_summary: str,
    difficulty: str,
) -> str:
    """
    Generate short markdown study notes for a topic.
    """

    if _client:
        response = _client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You write concise, well-structured markdown "
                        "study notes."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Write short study notes (roughly 200-300 words, "
                        f"markdown with headers and a bullet list) on "
                        f"'{topic_title}' pitched at a {difficulty} learner. "
                        f"Context: {topic_summary or 'N/A'}"
                    ),
                },
            ],
            temperature=0.6,
        )

        return response.choices[0].message.content.strip()

    return (
        f"## {topic_title} ({difficulty} level)\n\n"
        f"{topic_summary or 'No summary provided yet.'}\n\n"
        f"- Review the core definitions for {topic_title}.\n"
        f"- Work through at least one worked example.\n"
        f"- Attempt the {difficulty}-level practice quiz for this topic.\n"
        f"- Note anything unclear and revisit the source material.\n\n"
        f"_Offline study material is being used because no OPENAI_API_KEY "
        f"is configured._"
    )


# ---------------------------------------------------------------------------
# Offline question bank
# ---------------------------------------------------------------------------

def _template_questions(
    topic_title: str,
    difficulty: str,
    num_questions: int,
) -> List[dict]:
    """
    Offline fallback generator.

    Provides real educational questions without requiring an external
    AI API key.
    """

    question_bank = {

        # ===================================================================
        # VARIABLES & DATA TYPES
        # ===================================================================

        "Variables & Data Types": [
            {
                "prompt": (
                    "Which statement correctly assigns the integer value "
                    "10 to a variable in Python?"
                ),
                "option_a": "x = 10",
                "option_b": "int x = 10",
                "option_c": "integer x = 10",
                "option_d": "x := int 10",
                "correct_option": "A",
                "explanation": (
                    "Python variables are created by assigning a value using "
                    "the equals sign. The statement x = 10 stores the "
                    "integer 10 in the variable x."
                ),
            },
            {
                "prompt": (
                    "Which Python data type is used to store text?"
                ),
                "option_a": "int",
                "option_b": "str",
                "option_c": "float",
                "option_d": "bool",
                "correct_option": "B",
                "explanation": (
                    "The str data type represents text in Python. Strings "
                    "are normally written inside single or double quotation "
                    "marks."
                ),
            },
            {
                "prompt": (
                    "What is the data type of the value 3.14 in Python?"
                ),
                "option_a": "int",
                "option_b": "str",
                "option_c": "float",
                "option_d": "bool",
                "correct_option": "C",
                "explanation": (
                    "The value 3.14 contains a decimal point, so Python "
                    "treats it as a float. Integers such as 3 do not contain "
                    "a decimal part."
                ),
            },
            {
                "prompt": (
                    "Which value is a Boolean value in Python?"
                ),
                "option_a": '"True"',
                "option_b": "1",
                "option_c": "True",
                "option_d": '"False"',
                "correct_option": "C",
                "explanation": (
                    "True and False are Python Boolean values. Quoted "
                    "versions such as \"True\" are strings instead."
                ),
            },
            {
                "prompt": (
                    "What is the result of the following code? "
                    "x = 10; x = 20"
                ),
                "option_a": "x contains both 10 and 20",
                "option_b": "x contains 10",
                "option_c": "x contains 20",
                "option_d": "Python produces a syntax error",
                "correct_option": "C",
                "explanation": (
                    "The second assignment replaces the value previously "
                    "stored in x. Therefore, x contains 20 after the code "
                    "executes."
                ),
            },
            {
                "prompt": (
                    "Which function can be used to check the data type "
                    "of a value in Python?"
                ),
                "option_a": "type()",
                "option_b": "datatype()",
                "option_c": "typeof()",
                "option_d": "checktype()",
                "correct_option": "A",
                "explanation": (
                    "Python provides the built-in type() function to "
                    "determine the type of an object or value."
                ),
            },
            {
                "prompt": (
                    "Which of the following is a valid Python variable name?"
                ),
                "option_a": "2name",
                "option_b": "student-name",
                "option_c": "student_name",
                "option_d": "class",
                "correct_option": "C",
                "explanation": (
                    "Python variable names can contain letters, numbers, "
                    "and underscores but cannot begin with a number. "
                    "student_name follows these rules."
                ),
            },
            {
                "prompt": (
                    "What is the data type of the value 25?"
                ),
                "option_a": "float",
                "option_b": "int",
                "option_c": "str",
                "option_d": "bool",
                "correct_option": "B",
                "explanation": (
                    "25 is a whole number without a decimal component, "
                    "so Python represents it using the int data type."
                ),
            },
            {
                "prompt": (
                    "Which statement creates a string variable in Python?"
                ),
                "option_a": 'name = "Sabarish"',
                "option_b": "name = 100",
                "option_c": "name = True",
                "option_d": "name = 3.14",
                "correct_option": "A",
                "explanation": (
                    "Text enclosed in quotation marks is a string in Python. "
                    "Therefore, name = \"Sabarish\" creates a string variable."
                ),
            },
            {
                "prompt": (
                    "What does the int() function generally do in Python?"
                ),
                "option_a": "Converts a value to an integer when possible",
                "option_b": "Converts a value to a list",
                "option_c": "Creates a Boolean value only",
                "option_d": "Deletes a variable",
                "correct_option": "A",
                "explanation": (
                    "The int() function converts compatible values into "
                    "integers. For example, int(\"10\") produces the integer 10."
                ),
            },
        ],

        # ===================================================================
        # CONTROL FLOW
        # ===================================================================

        "Control Flow": [
            {
                "prompt": (
                    "Which keyword is used to execute code only when a "
                    "condition is true?"
                ),
                "option_a": "if",
                "option_b": "loop",
                "option_c": "check",
                "option_d": "when",
                "correct_option": "A",
                "explanation": (
                    "The if statement allows Python to execute a block of "
                    "code when a specified condition evaluates to True."
                ),
            },
            {
                "prompt": (
                    "Which keyword is commonly used to repeat code for "
                    "each item in a sequence?"
                ),
                "option_a": "repeat",
                "option_b": "foreach",
                "option_c": "for",
                "option_d": "loop",
                "correct_option": "C",
                "explanation": (
                    "Python uses the for loop to iterate over items in "
                    "sequences such as lists, strings, and ranges."
                ),
            },
            {
                "prompt": (
                    "What does the else block do in an if-else statement?"
                ),
                "option_a": "Always runs first",
                "option_b": "Runs when the if condition is false",
                "option_c": "Repeats the if condition",
                "option_d": "Stops Python completely",
                "correct_option": "B",
                "explanation": (
                    "The else block executes when the condition tested by "
                    "the if statement evaluates to False."
                ),
            },
            {
                "prompt": (
                    "Which keyword can immediately stop a loop?"
                ),
                "option_a": "stop",
                "option_b": "exit",
                "option_c": "break",
                "option_d": "end",
                "correct_option": "C",
                "explanation": (
                    "The break statement immediately terminates the loop "
                    "in which it appears."
                ),
            },
            {
                "prompt": (
                    "Which keyword skips the remaining statements in the "
                    "current loop iteration and continues with the next one?"
                ),
                "option_a": "skip",
                "option_b": "continue",
                "option_c": "next",
                "option_d": "pass",
                "correct_option": "B",
                "explanation": (
                    "The continue statement skips the remaining code in "
                    "the current iteration and moves to the next iteration."
                ),
            },
            {
                "prompt": (
                    "What values are produced by range(3) in a Python for loop?"
                ),
                "option_a": "1, 2, 3",
                "option_b": "0, 1, 2",
                "option_c": "0, 1, 2, 3",
                "option_d": "3 only",
                "correct_option": "B",
                "explanation": (
                    "range(3) starts at 0 and stops before 3. Therefore, "
                    "it produces 0, 1, and 2."
                ),
            },
        ],

        # ===================================================================
        # FUNCTIONS
        # ===================================================================

        "Functions": [
            {
                "prompt": (
                    "Which keyword is used to define a function in Python?"
                ),
                "option_a": "function",
                "option_b": "define",
                "option_c": "def",
                "option_d": "fun",
                "correct_option": "C",
                "explanation": (
                    "Python uses the def keyword to define a function. "
                    "The function name and parameters follow the keyword."
                ),
            },
            {
                "prompt": (
                    "Which keyword sends a value back from a Python function?"
                ),
                "option_a": "send",
                "option_b": "return",
                "option_c": "output",
                "option_d": "give",
                "correct_option": "B",
                "explanation": (
                    "The return statement sends a value back to the code "
                    "that called the function."
                ),
            },
            {
                "prompt": (
                    "What is a parameter in a Python function?"
                ),
                "option_a": (
                    "A variable received by a function through its definition"
                ),
                "option_b": "The name of the Python file",
                "option_c": "A type of loop",
                "option_d": "An error message",
                "correct_option": "A",
                "explanation": (
                    "A parameter is a variable listed in a function "
                    "definition. It receives a value when the function "
                    "is called."
                ),
            },
            {
                "prompt": (
                    "Which code correctly defines a function named greet?"
                ),
                "option_a": "function greet():",
                "option_b": "def greet():",
                "option_c": "create greet():",
                "option_d": "func greet():",
                "correct_option": "B",
                "explanation": (
                    "Python uses the def keyword followed by the function "
                    "name and parentheses to define a function."
                ),
            },
            {
                "prompt": (
                    "What does a function help you do in a Python program?"
                ),
                "option_a": (
                    "Reuse a block of code for a specific purpose"
                ),
                "option_b": "Only create variables",
                "option_c": "Only perform mathematical operations",
                "option_d": "Replace the Python interpreter",
                "correct_option": "A",
                "explanation": (
                    "Functions allow developers to organize reusable logic "
                    "into named blocks of code."
                ),
            },
        ],
    }

    # -----------------------------------------------------------------------
    # Find questions for the requested topic
    # -----------------------------------------------------------------------

    selected_questions = question_bank.get(topic_title)

    # -----------------------------------------------------------------------
    # Generic fallback for topics without a dedicated question bank
    # -----------------------------------------------------------------------

    if not selected_questions:
        selected_questions = [
            {
                "prompt": (
                    f"Which statement best describes the main purpose "
                    f"of {topic_title} in Python?"
                ),
                "option_a": (
                    f"It is used to apply concepts related to {topic_title}."
                ),
                "option_b": "It is only used for displaying images.",
                "option_c": "It replaces the Python interpreter.",
                "option_d": "It is unrelated to Python programming.",
                "correct_option": "A",
                "explanation": (
                    f"Option A is the most appropriate description because "
                    f"it directly relates to the purpose of {topic_title}."
                ),
            }
        ]

    # -----------------------------------------------------------------------
    # Shuffle questions
    # -----------------------------------------------------------------------

    questions = selected_questions.copy()
    random.shuffle(questions)

    # -----------------------------------------------------------------------
    # Return requested number of questions
    # -----------------------------------------------------------------------

    return questions[:min(num_questions, len(questions))]
