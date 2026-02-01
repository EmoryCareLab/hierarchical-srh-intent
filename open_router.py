import os
import json
import re
import time
import pandas as pd
from openai import OpenAI
from utils import load_existing_results,save_result_incrementally



# --------------------
# CONFIG
# --------------------
input_file = "data/hinglish/final_jmir_data/cleaned_data_for_jmir.xlsx" 
output_json_file = "output/sarvam-m.json"

# Models = [
#     "openai/gpt-4o",
#     "openai/gpt-5",
#     "meta-llama/llama-3.1-8b-instruct",
#     "meta-llama/llama-3.3-70b-instruct", 
#     "google/gemma-2-9b-it",
#     "google/gemma-3-27b-it", 
#     "qwen/qwen-2.5-7b-instruct", 
#     "mistralai/mixtral-8x7b-instruct",
#     "anthropic/claude-3.5-sonnet", 
    #   "sarvamai/sarvam-m"
# ]

MODEL = "sarvamai/sarvam-m"
MAX_RETRIES = 2

# --------------------
# OPENROUTER CLIENT
# --------------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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"
)

hierarchy = {
    "Contraception and Family Planning": [
        "Effectiveness and Duration",
        "Family Planning Queries",
        "Side Effects",
        "Sterilization",
        "Types of Contraceptives",
        "Usage Guidance"
    ],
    "Menstrual Health": [
        "Menstrual Cycle Information",
        "Menstrual Flow",
        "Period Pain Management",
        "Sanitary Products and Hygiene"
    ],
    "Pregnancy and PNC": [
        "Abortion",
        "Antepartum",
        "Breastfeeding",
        "Infertility",
        "Miscarriage",
        "Postpartum",
        "Pregnancy Information"
    ], 
    "Sexual and Vaginal Health": [
        "Sex-Related Queries",
        "Reproductive Anatomy",
        "STI/STD",
        "UTI",
        "Vaginal Health and Discharge",
        "Vaginal or Uterine Infections"
    ],
    "PCOS or PCOD": [
        "Information", 
        "Management", 
        "Symptoms"
    ],
    "HIV": [
        "Prevention",
        "Stigma and Awareness",
        "Symptoms and Early Detection",
        "Treatment"
    ],
    "Mental Health and Wellness": [
        "Information and Safety Concerns",
        "Stress Management"
    ],
    "Other": [
        "Child Health",
        "Cultural, Religious, or Moral Norms",
        "Diet and Nutrition",
        "Exercise and Fitness",
        "General Health Queries",
        "Health Equity and Access",
        "Marriage & Relationships",
        "Misconceptions and Myths"
    ]
}

# --------------------
# PROMPT CREATOR
# --------------------
# def create_prompt(query: str) -> str:
#     return f"""
# Classify the following Hinglish (Romanized Hindi + English) query into exactly ONE topic and ONE subtopic from the intent hierarchy below.

# ### Intent Hierarchy:
# {json.dumps(hierarchy, indent=4, ensure_ascii=False)}

# **Query (Hinglish):** "{query}"

# **Output Format:**
# "Topic: <selected_topic> Subtopic: <selected_subtopic_from_that_topic>"

# ### Rules:
# 1. Select ONLY ONE topic and ONE subtopic.
# 2. The subtopic MUST belong to the selected topic.
# 3. DO NOT generate any additional text, explanations, or code.
# 4. Strictly follow the output format.
# """.strip()

def create_prompt(query: str) -> str:
    return f"""
Classify the following Hinglish (Romanized Hindi + English) query into exactly ONE topic and ONE subtopic from the intent hierarchy below.

### Intent Hierarchy:
{json.dumps(hierarchy, indent=4, ensure_ascii=False)}

**Query (Hinglish):** "{query}"

**Output Format:**
Return your answer inside a JSON code block like this:

```json
{{
  "Topic": "<selected_topic>",
  "Subtopic": "<selected_subtopic_from_that_topic>",
  "Confidence": <number between 0.0 and 1.0>,
  "Reason": "<short reason>"
}}
```
# Rules:
1. Select ONLY ONE topic and ONE subtopic.
2. The subtopic MUST belong to the selected topic.
3. Confidence MUST be a decimal number between 0.0 and 1.0.
4. Reason MUST be a short sentence (max 20 words).
5. Output MUST be valid JSON inside a JSON code block.

# Final instruction
Return just the json object in markdown format. Do not include any other text in the response.
""".strip()


def extract_json_from_markdown(output: str) -> dict:
    """
    Extract JSON from a markdown-formatted string.
    Works for both ```json ... ``` blocks and plain JSON text.
    """
    match = re.search(r"json\s*(\{.*?\})\s*", output, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            return {}
    else:
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            return {}

# --------------------
# CLASSIFICATION WITH RETRIES
# --------------------
def classify_with_retry(question: str):
    prompt = create_prompt(question)
    # print("prompt = ",prompt)
    for attempt in range(MAX_RETRIES + 1):
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "You are an SRH intent classification system. Follow instructions exactly."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            raw_output = completion.choices[0].message.content.strip()
            parsed = extract_json_from_markdown(raw_output)
            if parsed and parsed.get("Topic"):
                return {
                    "Topic": parsed.get("Topic"),
                    "Subtopic": parsed.get("Subtopic"),
                    "Confidence": parsed.get("Confidence"),
                    "Reason": parsed.get("Reason"),
                    "Raw_Output": raw_output
                }
            else:
                raise ValueError("Parsed output is empty or missing Topic/Subtopic.") # will retry the same query 
        except Exception as e:
            if attempt < MAX_RETRIES:
                wait_time = 1.5 * (attempt + 1)
                print(f"[Retry {attempt+1}] Error: {e} — retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                return {
                "Topic": None,
                "Subtopic": None,
                "Confidence": None,
                "Reason": None,
                "Raw_Output": f"[ERROR] {e}"
            }
# --------------------
# PROCESS CSV
# --------------------
def main():
    # query = "Emergency garbhnirodhak dawaai ke alawa aur kya options hain?"
    # classification = classify_with_retry(query)
    # print(classification)

    # Load dataset
    df = pd.read_excel(input_file)

    results = load_existing_results(output_json_file)
    processed_indexes = {r["Index"] for r in results}
    
    # Process each query
    for ind, row in df.iterrows():
        Index = row['Index']
        query = row['User Content']

        if Index in processed_indexes:
            print(f"Query already processed Index: {Index}")
            continue
    
        result = classify_with_retry(query)

        topic = result["Topic"]
        subtopic = result["Subtopic"]
        confidence = result["Confidence"]
        reason = result["Reason"]
        raw_output = result['Raw_Output']

        save_result_incrementally(
            existing_results=results,
            output_file=output_json_file, 
            Index=Index,
            query=query,
            topic=topic,
            subtopic=subtopic,
            confidence=confidence,
            reason=reason,
            raw_output=raw_output,
            model=MODEL
        )
        print(f"{ind=}, {Index=}, {query=}")
        time.sleep(3)  # Small delay to avoid rate limits
        break

if __name__ == "__main__":
    main()