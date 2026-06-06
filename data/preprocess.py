import pandas as pd
import os
import re
import json

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)
    # Remove URLs
    text = re.sub(r'http[s]?://\S+', '', text)
    # Remove special characters but keep some punctuation
    text = re.sub(r'[^a-zA-Z0-9가-힣\s\.,!\?]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def process_thn():
    print("Processing TheHackerNews_Dataset.csv...")
    path = 'data/raw/TheHackerNews_Dataset.csv'
    if not os.path.exists(path): return pd.DataFrame()
    
    df = pd.read_csv(path)
    df['text'] = (df['Title'].fillna('') + " " + df['Article'].fillna('')).apply(clean_text)
    
    def map_label(row):
        text = row['text'].lower()
        if 'ransomware' in text: return 'ransomware'
        if any(kw in text for kw in ['crypto', 'bitcoin', 'ethereum', 'exchange', 'wallet']): return 'crypto_crime'
        if any(kw in text for kw in ['stalking', 'spyware', 'stalkerware']): return 'stalking'
        
        orig_label = row['Label']
        label_map = {
            'Data_Breaches': 'hacking',
            'Malware': 'malware',
            'Vulnerability': 'hacking',
            'Cyber_Attack': 'hacking'
        }
        return label_map.get(orig_label, 'hacking')

    df['label'] = df.apply(map_label, axis=1)
    return df[['text', 'label']]

def process_nigerian_fraud():
    print("Processing Nigerian_Fraud.csv...")
    path = 'data/raw/Nigerian_Fraud.csv'
    if not os.path.exists(path): return pd.DataFrame()
    
    df = pd.read_csv(path)
    df['text'] = (df['subject'].fillna('') + " " + df['body'].fillna('')).apply(clean_text)
    df['label'] = 'fraud'
    return df[['text', 'label']]

def process_phishing_email():
    print("Processing phishing_email.csv...")
    path = 'data/raw/phishing_email.csv'
    if not os.path.exists(path): return pd.DataFrame()
    
    df = pd.read_csv(path)
    # label 1: phishing, 0: safe
    df = df[df['label'] == 1].copy()
    df['text'] = df['text_combined'].apply(clean_text)
    df['label'] = 'phishing'
    return df[['text', 'label']]

def process_reddit():
    print("Processing Reddit_cybersecurity.json...")
    path = 'data/raw/Reddit_cybersecurity.json'
    if not os.path.exists(path): return pd.DataFrame()
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if isinstance(data, list):
        texts = [clean_text(t) for t in data if len(t) > 50] # Filter short ones
        df = pd.DataFrame({'text': texts, 'label': 'hacking'})
        return df
    return pd.DataFrame()

def main():
    if not os.path.exists('data/processed'):
        os.makedirs('data/processed')
        
    all_dfs = []
    
    all_dfs.append(process_thn())
    all_dfs.append(process_nigerian_fraud())
    all_dfs.append(process_phishing_email())
    all_dfs.append(process_reddit())
    
    combined_df = pd.concat([df for df in all_dfs if not df.empty], ignore_index=True)
    
    # Shuffle
    combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    output_path = 'data/processed/news_eye_dataset.csv'
    combined_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"✅ Preprocessing complete. Saved to {output_path}")
    print(f"Total samples: {len(combined_df)}")
    print(combined_df['label'].value_counts())

if __name__ == "__main__":
    main()
