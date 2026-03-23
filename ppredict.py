from transformers import AdamW, get_linear_schedule_with_warmup, BertTokenizer

import torch
import numpy as np
import random
from torch.utils.data import DataLoader, TensorDataset
import torch.nn.functional as F
import torch.optim as optim
import numpy as np
import json
import numpy as np
import random
from tqdm import tqdm
from sklearn.metrics import accuracy_score, f1_score, classification_report
from model import BERT_SENTIMENT
import csv
import warnings
import pandas as pd


# 忽略所有警告
warnings.filterwarnings("ignore")
from transformers import BertTokenizer
import torch
import json
from model import BERT_SENTIMENT
import os


# Load configuration
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Initialize tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-chinese")
max_length = config["max_length"]


def get_data(text):
    x = tokenizer.encode_plus(
        text,
        max_length=max_length,
        truncation=True,
        padding="max_length"
    )
    input_ids = torch.tensor(x["input_ids"]).unsqueeze(0)  # No need to unsqueeze for batch
    attention_mask = torch.tensor(x["attention_mask"]).unsqueeze(0)  # No need to unsqueeze for batch
    if torch.cuda.is_available():
        input_ids = input_ids.cuda()
        attention_mask = attention_mask.cuda()
    return input_ids, attention_mask


def predict(fileName):

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(BASE_DIR, 'spiders', '{}cleaned.csv'.format(fileName))
    # Load model
    model = BERT_SENTIMENT()
    # model = torch.load("output/0.6938573181116661.pth", map_location=torch.device('cuda'))
    model.load_state_dict(torch.load("output/0.9330007097157856.pth", map_location=torch.device('cuda')))
    model.eval()
    if torch.cuda.is_available():
        model.cuda()

    input_file = filepath
    output_file = "output_data/clean_result.csv"
    print("模型判断中....")
    with open(input_file, "r", encoding="utf-8") as file:
        next(file)
        texts = file.readlines()

    emo = []

    for text in texts:
        z = text.split(',')
        # Process input text
        input_ids, attention_mask = get_data(z[0])

        # Perform inference
        logits_ = model(input_ids, attention_mask)
        _, predict = torch.max(logits_.data, 1)
        emo.append(predict.item())

    # Save results

    df_original = pd.read_csv(input_file)
    df_original['Emotion'] = emo

    # Save results
    df_original.to_csv(output_file, index=False, encoding='utf-8')


def pre(text):
    model = BERT_SENTIMENT()
    model.load_state_dict(torch.load("output/0.9330007097157856.pth", map_location=torch.device('cuda')))
    model.eval()
    if torch.cuda.is_available():
        model.cuda()
    print("模型判断中....")
    input_ids, attention_mask = get_data(text)
    logits_ = model(input_ids, attention_mask)
    _, predict = torch.max(logits_.data, 1)
    print(predict.item())
    return predict.item()


if __name__ == '__main__':
    # 加载bert模型
    key = "12306被质疑纵容买长乘短"
    predict(key)