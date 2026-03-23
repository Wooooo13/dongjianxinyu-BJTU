import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset
from transformers import BertTokenizer
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

data = pd.read_csv("data/data.csv", sep="\t")

data_train, data_test = train_test_split(data, test_size=0.35)
tokeizer = BertTokenizer.from_pretrained("bert-base-chinese",add_special_tokens=True)

#print(data_train)
#每一行转换成列表
train_list = data_train.values.tolist()
test_list = data_test.values.tolist()
train_list_feature = [list[:-1] for list in train_list]
train_list_label = [list[-1] for list in train_list]
test_list_feature = [list[:-1] for list in test_list]
test_list_label = [list[-1] for list in test_list]
# print(train_list_label)
max_length = config["max_length"]

def text2input_data(train_list_feature):
    input_ids_all = []
    attention_mask_all = []
    for train_list in train_list_feature:
        if not train_list:
            continue  # 跳过空列表
        #print(train_list[0])
        text = train_list[0]


        x = tokeizer.encode_plus(
            text,
            max_length=max_length,
            truncation=True,
            padding="max_length"
        )
        input_ids = x["input_ids"]
        len_ = len(input_ids)
        input_ids = input_ids + [0]*(max_length - len_)
        attention_mask = [1] * len_ + [0] * (max_length - len_)
        input_ids_all.append(input_ids)
        attention_mask_all.append(attention_mask)
    return input_ids_all,attention_mask_all



train_input_ids,train_attention_mask = text2input_data(train_list_feature)
dev_input_ids,dev_attention_mask = text2input_data(test_list_feature)
# train_list_label
# test_list_label
train_input_ids = torch.Tensor(train_input_ids)
train_attention_mask = torch.Tensor(train_attention_mask)
train_label = torch.Tensor(train_list_label)



dev_input_ids = torch.Tensor(dev_input_ids)
dev_attention_mask = torch.Tensor(dev_attention_mask)
dev_label = torch.Tensor(test_list_label)

train_dateset = TensorDataset(train_input_ids,train_attention_mask,train_label)
test_dateset = TensorDataset(dev_input_ids,dev_attention_mask,dev_label)

train_iter = torch.utils.data.DataLoader(train_dateset, config["train_batch_size"], shuffle=True)
test_iter = torch.utils.data.DataLoader(test_dateset, config["dev_batch_size"], shuffle=True)


def get_train_data():
    return train_iter
def get_test_data():
    return test_iter