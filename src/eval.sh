python3 -m src.run_intent \
  --input_file "data/hinglish/final_jmir_data/cleaned_data_for_jmir.xlsx" \
  --output_file "output/gpt-5.json" \
  --model "openai/gpt-5" \
  --max_retries 3 \
  --sleep 2 \
#   --max_rows "None"
