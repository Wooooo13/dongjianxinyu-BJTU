from model import BERT_SENTIMENT
from dataloader import get_train_data,get_test_data
import pandas as pd
import torch
import torch.optim as optim
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset
from transformers import BertTokenizer
import numpy as np
import json
from tqdm import tqdm
import warnings
from sklearn.metrics import accuracy_score, f1_score, classification_report


# 忽略所有警告
warnings.filterwarnings("ignore")

def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    #pd.seed(seed)  # 设置 Pandas 使用的随机种子
with open("config.json", "r") as config_file:
    config = json.load(config_file)
# 设置种子
setup_seed(42)


USE_CUDA = torch.cuda.is_available()
if USE_CUDA:
    print("using GPU")

def dev(model,dev_iter):
    predicted_all = np.array([])
    label_all = np.array([])
    loop = tqdm((dev_iter), total=len(dev_iter))
    for input_id, attention_mask, label in loop:
        if USE_CUDA:
            input_id = input_id.long().cuda()
            attention_mask = attention_mask.long().cuda()
            label = label.long().cuda()
        else:
            input_id = input_id.long()
            attention_mask = attention_mask.long()
            label = label.long()
        _, logits_ = model(input_id, attention_mask, label)
        _, predict = torch.max(logits_.data, 1)
        predicted_ = predict.cpu().numpy()
        label_ = label.cpu().numpy()
        predicted_all = np.append(predicted_all, predicted_)
        label_all = np.append(label_all, label_)
    class_report = classification_report(label_all, predicted_all,digits=4)
    f1 = f1_score(label_all, predicted_all, average='weighted')
    print(class_report)
    return f1


def train(model,train_iter,dev_iter):
    global max_f1
    max_f1 = config["min_f1"]

    model = BERT_SENTIMENT()
    if USE_CUDA:
        model = model.cuda()
    # model.load_state_dict(torch.load('output/0.9279516529736584.pth', map_location=torch.device('cuda')))

    model.train()
    lr = config["lr"]
    epochs = config["epochs"]
    optimizer = optim.Adam(model.parameters(),lr=lr,weight_decay=0)
    for epoch in range(epochs):
        predicted_all = np.array([])
        label_all = np.array([])
        loop = tqdm((train_iter),total=len(train_iter))
        for input_ids,attention_mask,label in loop:
            optimizer.zero_grad()
            if USE_CUDA:
                input_ids = input_ids.long().cuda()
                attention_mask = attention_mask.long().cuda()
                label = label.long().cuda()
            else:
                input_ids = input_ids.long()
                attention_mask = attention_mask.long()
                label = label.long()
            loss, logits = model(input_ids,attention_mask,label)
            loop.set_postfix(loss=f'{round(loss.item(), 5)}')
            loss.backward()
            optimizer.step()
            _, predict = torch.max(logits.data, 1)
            predicted_ = predict.cpu().numpy()
            label_ = label.cpu().numpy()
            # print(predicted_)
            # print(label_)
            predicted_all = np.append(predicted_all, predicted_)

            label_all = np.append(label_all, label_)
        # print(predicted_all)
        # print(label_all)
        f1 = f1_score(label_all, predicted_all, average='weighted')
        print("\n", "epoch ", str(epoch + 1), "number of f1:", str(f1))
        dev_f1 = dev(model, dev_iter)
        # torch.save(model, "output/" + str(dev_f1) + ".pth")
        # torch.save(model.state_dict(), "output/" + str(dev_f1) + ".pth")
        # print("\n", "new model was saved")
        if dev_f1 > max_f1:
            #保存模型
            max_f1 = dev_f1
            # torch.save(model,"output/"+str(dev_f1)+".pth")
            torch.save(model.state_dict(), "output/" + str(dev_f1) + ".pth")
            print("\n","new model was saved")



if __name__ == "__main__":
    model = BERT_SENTIMENT()
    if USE_CUDA:
        model = model.cuda()
    train_iter = get_train_data()
    dev_iter = get_test_data()
    train(model,train_iter,dev_iter)

