import fasttext
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt

# Load the FastText model
model = fasttext.load_model('lid.176.bin')
input_file = "./data/hinglish/final_jmir_data/cleaned_data_for_jmir.xlsx" 

NON_ALPHA_RE = re.compile(r"[^a-zA-Z]+")

def tokenize_lexical(text: str):
    """
    Returns only lexical alphabetic tokens (roman letters).
    """
    tokens = []
    for tok in str(text).split():
        tok = tok.lower()
        tok = NON_ALPHA_RE.sub("", tok)  # remove punctuation/numbers
        if tok:
            tokens.append(tok)
    return tokens

def calculate_cmi(sentence):
    tokens = str(sentence).split()
    # print("tokens = ", tokens)
    n = len(tokens)
    lex_tokens = tokenize_lexical(sentence)  # lexical tokens -> n-u
    
    if n == 0:
        return 0, {'hi': 0, 'en': 0}
    
    lang_counts = {'hi': 0, 'en': 0}
    
    for token in lex_tokens:
        # FastText predicts on whole words
        prediction = model.predict(token, k=1)
        print(token, prediction)
        lang = prediction[0][0].replace('__label__', '')
        
        # if lang == 'hi':
        #     lang_counts['hi'] += 1
        if lang == 'en':
            lang_counts['en'] += 1
        else:
            lang_counts['hi'] += 1
    
    max_count = max(lang_counts['hi'], lang_counts['en'])
    cmi = 100 * (1 - max_count / n)
    
    return cmi, lang_counts

# Process all 4000 sentences
def process_corpus(df):
    results = []
    
    for idx, row in df.iterrows():
        query_id = row['Index']
        query = row['User Content']

        print(query_id, query)
        
        # Calculate CMI
        cmi, lang_counts = calculate_cmi(query)
        
        # Store results
        results.append({
            'id': query_id,
            'query': query,
            'cmi': cmi, 
            'lang_counts': lang_counts
        })
        # print(results)
        
        # Progress update
        if (idx + 1) % 500 == 0:
            print(f"Processed {idx + 1} queries...")
    
    return pd.DataFrame(results)


# Read Excel file
print("Reading Excel file...")
df_input = pd.read_excel(input_file)
df_input = df_input[['Index', "User Content"]]
# df_input = df_input[71:75]

# Check column names
print(f"Columns: {df_input.columns.tolist()}")

print("Processing queries...")
df_results = process_corpus(df_input)

print(df_results)

# Calculate statistics
print("\n" + "="*50)
print("CMI STATISTICS")
print("="*50)
print(f"Total sentences: {len(df_results)}")
print(f"Mean CMI: {df_results['cmi'].mean():.2f}%")
print(f"Median CMI: {df_results['cmi'].median():.2f}%")
print(f"Std Dev: {df_results['cmi'].std():.2f}%")
print(f"Min CMI: {df_results['cmi'].min():.2f}%")
print(f"Max CMI: {df_results['cmi'].max():.2f}%")
print("="*50)

# Save results to CSV
df_results.to_csv('./output/cmi_results.csv', index=False, encoding='utf-8')
print("\nResults saved to 'cmi_results.csv'")


# Histogram of CMI distribution
plt.figure(figsize=(10, 6))
plt.hist(df_results['cmi'], bins=50, edgecolor='black', alpha=0.7)
plt.xlabel('CMI (%)')
plt.ylabel('Frequency')
plt.title('Distribution of Code-Mixing Index across 4000 Sentences')
plt.grid(True, alpha=0.3)
plt.savefig('./figures/cmi_distribution.png', dpi=300, bbox_inches='tight')
print("Histogram saved to 'cmi_distribution.png'")

# Show some examples
print("\n" + "="*50)
print("SAMPLE RESULTS")
print("="*50)
print(df_results.head(10).to_string(index=False))