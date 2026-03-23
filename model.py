import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset
from transformers import BertTokenizer,BertModel
import numpy as np
import json
def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    #pd.seed(seed)  # 设置 Pandas 使用的随机种子
with open("config.json", "r") as config_file:
    config = json.load(config_file)
# 设置种子
setup_seed(42)

class BERT_SENTIMENT(nn.Module):
    def __init__(self):
        super(BERT_SENTIMENT, self).__init__()
        self.encoder = BertModel.from_pretrained("bert-base-chinese")
        self.Linear = nn.Linear(768,7)

        self.CrossEntropyLoss = nn.CrossEntropyLoss(reduction="mean")
        self.num_labels = 7
    def forward(self,input_ids,attention_mask,label=None):
        x = self.encoder(input_ids,attention_mask)[0]
        x = x[:,0,:]  #[4,768]
        logits = self.Linear(x)
        # logits = self.Linear2(x)

        if label == None:
            return logits
        if label != None:
            loss = self.CrossEntropyLoss(logits,label)
            return loss,logits
# 自定义
    def copy(self):
        copy_model = BERT_SENTIMENT()  # 创建一个新的模型实例
        copy_model.load_state_dict(self.state_dict())  # 复制当前模型的参数状态
        return copy_model
