import json
import time
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI
from generate import ask_question

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

# Setup the Judge LLM
judge_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# fast model for the judge
# JUDGE_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
JUDGE_MODEL = "openai/gpt-oss-20b:free"

with open("ground_truth.json", "r") as f:
    ground_truth = json.load(f)

total_score = 0
total_questions = len(ground_truth)

logging.info(f"starting LLM Evaluation for {total_questions} questions\n")

for item in ground_truth:
    question = item["question"]
    correct_answer = item["answer"]

    logging.info(f"Q: {question}")

    # Generate
    generated_answer = ask_question(question)
    logging.info(f"Generated: {generated_answer}")

    # Ask the Judge to score
    judge_prompt = f"""
        You are an expert evaluator.
        Question: {question}
        Correct Answer: {correct_answer}
        Generated Answer: {generated_answer}

        Does the Generated Answer contain the correct facts from the Correct Answer?
        Return ONLY a valid JSON object: {{"score": 1}} for yes, or {{"score": 0}} for no.
        """

    response = judge_client.chat.completions.create(
        model=JUDGE_MODEL,
        messages=[{"role": "user", "content": judge_prompt}]
    )

    # Parse the Judge's score
    try:
        if not response.choices:
            continue

        judge_json = json.loads(response.choices[0].message.content)

        # Add the score to our total
        score = judge_json.get("score", 0)
        total_score += score
        logging.info(f"Judge Score: {score}\n")

    except Exception as e:
        logging.error(f"Judge failed to return JSON: {e}\n")

    logging.info("Sleep for 3 seconds to avoid rate limits")
    time.sleep(3)
# Final Math
accuracy = (total_score / total_questions) * 100
logging.info(f"=== FINAL LLM ACCURACY: {accuracy}% ===")
