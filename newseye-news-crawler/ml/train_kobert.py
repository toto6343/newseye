import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, AdamW, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from tqdm import tqdm
import os

# Configuration
MODEL_NAME = "monologg/kobert" # Or 'bert-base-multilingual-cased' as fallback
DATA_PATH = "data/processed/news_eye_dataset.csv"
OUTPUT_DIR = "newseye-news-crawler/ml/saved_model"
MAX_LEN = 128
BATCH_SIZE = 16
EPOCHS = 3
LEARNING_RATE = 2e-5

class NewsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        label = self.labels[item]

        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt',
        )

        return {
            'text': text,
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }

def train():
    print("Loading data...")
    df = pd.read_csv(DATA_PATH)
    
    # Use a small subset for CPU training demonstration if needed
    # df = df.sample(2000) 
    
    le = LabelEncoder()
    df['label_encoded'] = le.fit_transform(df['label'])
    num_labels = len(le.classes_)
    
    # Save label encoder classes
    with open(os.path.join("newseye-news-crawler/ml", "labels.txt"), "w") as f:
        f.write("\n".join(le.classes_))

    train_df, val_df = train_test_split(df, test_size=0.1, random_state=42)

    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    
    train_dataset = NewsDataset(
        texts=train_df.text.to_numpy(),
        labels=train_df.label_encoded.to_numpy(),
        tokenizer=tokenizer,
        max_len=MAX_LEN
    )

    val_dataset = NewsDataset(
        texts=val_df.text.to_numpy(),
        labels=val_df.label_encoded.to_numpy(),
        tokenizer=tokenizer,
        max_len=MAX_LEN
    )

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    model = BertForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=num_labels)
    model = model.to(device)

    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE, correct_bias=False)
    total_steps = len(train_loader) * EPOCHS

    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=0,
        num_training_steps=total_steps
    )

    for epoch in range(EPOCHS):
        print(f"Epoch {epoch + 1}/{EPOCHS}")
        model.train()
        total_loss = 0
        
        for batch in tqdm(train_loader):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            outputs = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )

            loss = outputs.loss
            total_loss += loss.item()

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

        avg_train_loss = total_loss / len(train_loader)
        print(f"Average training loss: {avg_train_loss}")

    # Save model
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"Model saved to {OUTPUT_DIR}")

if __name__ == "__main__":
    train()
