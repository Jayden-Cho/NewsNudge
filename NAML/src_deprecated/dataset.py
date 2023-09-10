from torch.utils.data import Dataset
import pandas as pd
from ast import literal_eval
from os import path
import numpy as np
from config import model_name
import importlib
import torch

try:
    config = getattr(importlib.import_module('config'), f"{model_name}Config")
except AttributeError:
    print(f"{model_name} not included!")
    exit()


class BaseDataset(Dataset):
    def __init__(self, behaviors_path, news_path):
        # call the constructor of the parent class and ensure proper initialization of 
        # inherited attributes and behavior before adding any custom initialization 
        # specific to the subclass.
        super(BaseDataset, self).__init__()

        # NAML만 쓸꺼면 굳이 필요없을 듯.
        assert all(attribute in [
            'category', 'subcategory', 'title', 'abstract', 'title_entities',
            'abstract_entities'
        ] for attribute in config.dataset_attributes['news'])
        assert all(attribute in ['user', 'clicked_news_length']
                   for attribute in config.dataset_attributes['record'])

        self.behaviors_parsed = pd.read_table(behaviors_path)
        # NAML에서는 category, subcategory, title, abstract 총 네 가지 feature 사용.
        self.news_parsed = pd.read_table(
            news_path,
            index_col='id',
            usecols=['id'] + config.dataset_attributes['news'],
            converters={
                attribute: literal_eval
                for attribute in set(config.dataset_attributes['news']) & set([
                    'title', 'abstract', 'title_entities', 'abstract_entities'
                ])
            })
        
        # 데이터셋 크기를 줄이려면 behaviors_parsed랑 news_parsed의 양을 줄이기.
        # 아래 코드 사용.
        self.behaviors_parsed = self.behaviors_parsed.iloc[:100]
        # self.news_parsed = self.news_parsed.iloc[:1000]

        self.news_id2int = {x: i for i, x in enumerate(self.news_parsed.index)}
        self.news2dict = self.news_parsed.to_dict('index')
        for key1 in self.news2dict.keys():
            for key2 in self.news2dict[key1].keys():
                self.news2dict[key1][key2] = torch.tensor(
                    self.news2dict[key1][key2])
        padding_all = {
            'category': 0,
            'subcategory': 0,
            'title': [0] * config.num_words_title,
            'abstract': [0] * config.num_words_abstract,
            'title_entities': [0] * config.num_words_title,
            'abstract_entities': [0] * config.num_words_abstract
        }
        for key in padding_all.keys():
            padding_all[key] = torch.tensor(padding_all[key])

        self.padding = {
            k: v
            for k, v in padding_all.items()
            if k in config.dataset_attributes['news']
        }

    def __len__(self):
        return len(self.behaviors_parsed)

    # clicked_news라는 사용 기록을 가진 user가
    # candidate_news라는 후보 기사들 중 어떤 것을 봤는지 추측하는 task.
    # 정답은 clicked.
    def __getitem__(self, idx):
        item = {}
        row = self.behaviors_parsed.iloc[idx]
        if 'user' in config.dataset_attributes['record']:
            item['user'] = row.user
        item["clicked"] = list(map(int, row.clicked.split()))
        item["candidate_news"] = [
            self.news2dict[x] for x in row.candidate_news.split()
        ]
        # config.num_clicked_news_a_user가 50이므로 최대 50개 기록만 사용.
        item["clicked_news"] = [
            self.news2dict[x]
            for x in row.clicked_news.split()[:config.num_clicked_news_a_user]
        ]
        if 'clicked_news_length' in config.dataset_attributes['record']:
            item['clicked_news_length'] = len(item["clicked_news"])
        repeated_times = config.num_clicked_news_a_user - \
            len(item["clicked_news"])
        assert repeated_times >= 0
        # 여기서 padding을 하는 이유?
        # item length를 data마다 동일하게 하기 위해?
        item["clicked_news"] = [self.padding
                                ] * repeated_times + item["clicked_news"]

        return item
