import json
import os
import argparse

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

# Load existing results
def load_existing_results(output_file):
    """Loads existing classification results to avoid re-processing."""
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading existing results: {str(e)}")
            return []
    return []

def save_result_incrementally(existing_results, output_file, Index, query, topic, subtopic, confidence, reason, raw_output, model):

    existing_results.append(
        {
            "Index": Index, 
            "query": query,
            "topic": topic,
            "subtopic": subtopic,
            "confidence": confidence, 
            "reason": reason,
            "raw_output": raw_output, 
            "model": model
        }
    )
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(existing_results, f, indent=4, ensure_ascii=False)
        print(f"Saved classification for query: {query}")
    except Exception as e:
        print(f"Error saving result: {str(e)}")

# Function: Append result and save immediately
def append_and_save_result(new_result, file_path, all_results):
    all_results.append(new_result)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

def parse_args():
    parser = argparse.ArgumentParser(
        description="SRH Hinglish intent classification"
    )

    parser.add_argument(
        "--input_file",
        type=str,
        default="data/hinglish/final_jmir_data/cleaned_data_for_jmir.xlsx",
        help="Path to input Excel file"
    )

    parser.add_argument(
        "--output_file",
        type=str,
        default="output/sarvam-m.json",
        help="Path to output JSON file"
    )

    parser.add_argument(
        "--model",
        type=str,
        default="sarvamai/sarvam-m",
        help="Model name"
    )

    parser.add_argument(
        "--max_retries",
        type=int,
        default=2,
        help="Maximum retries per query"
    )

    parser.add_argument(
        "--sleep",
        type=float,
        default=3.0,
        help="Sleep time (seconds) between API calls"
    )

    parser.add_argument(
        "--max_rows",
        type=int,
        default=None,
        help="Optional limit on number of rows to process"
    )

    return parser.parse_args()
