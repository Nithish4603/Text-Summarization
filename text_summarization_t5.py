# -*- coding: utf-8 -*-
"""Text_summarization_T5.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1M97FgZc8qA0GqxoEhlh57WWPPHvEOLn_
"""

from google.colab import drive
drive.mount('/content/drive')

import nltk

print('The nltk version is {}.'.format(nltk.__version__))

import numpy as np 
import pandas as pd

!pip install -U nltk

"""Importing the Dataset"""

summary = pd.read_csv('/content/drive/MyDrive/training/news_summary.csv', encoding='iso-8859-1')
raw = pd.read_csv('/content/drive/MyDrive/training/news_summary_more.csv', encoding='iso-8859-1')

pre_data1 =  raw.iloc[:,0:2].copy()
pre_data2 = summary.iloc[:,0:6].copy()
pre_data2['text'] = pre_data2['author'].str.cat(pre_data2['date'].str.cat(pre_data2['read_more'].str.cat(pre_data2['text'].str.cat(pre_data2['ctext'], sep = " "), sep =" "),sep= " "), sep = " ")

#taking only the required columns
pre_data = pd.DataFrame()
pre_data['text'] = pd.concat([pre_data1['text'], pre_data2['text']], ignore_index=True)
pre_data['summary'] = pd.concat([pre_data1['headlines'],pre_data2['headlines']],ignore_index = True)

pre_data.head(2)

pre_data = pre_data.dropna()
pre_data.head()

#renaming the column names
pre_data = pre_data.rename(columns={'text': 'source_text', 'summary': 'target_text'})
pre_data

#adding prefix "summarize" to the source_text column
pre_data['source_text'] = "summarize: " + pre_data['source_text']

pre_data

len(pre_data)

#As the dataset is very large we are considering only first 25000 rows for our training data
main_data = pre_data[:25000]
#we are considering 1000 rows for test data
test_data = pre_data[25001:26001]

len(main_data)

len(test_data)

pip install --upgrade simplet5

#splitting the data
from sklearn.model_selection import train_test_split
train_df, eval_df = train_test_split(main_data, test_size=0.1)
train_df.shape, eval_df.shape

# import
from simplet5 import SimpleT5

# instantiate
model = SimpleT5()

import torch
torch.cuda.empty_cache()

# load (supports t5, mt5, byT5 models)
model.from_pretrained("t5","t5-base")

# train
model.train(train_df=train_df, # pandas dataframe with 2 columns: source_text & target_text
            eval_df=eval_df, # pandas dataframe with 2 columns: source_text & target_text
            source_max_token_len = 256, 
            target_max_token_len = 128,
            batch_size = 8,
            max_epochs = 2,
            use_gpu = True,
            outputdir = "outputs",
            early_stopping_patience_epochs = 0,
            precision = 32
            )

model.load_model("t5","/content/outputs/simplet5-epoch-1-train-loss-1.0591-val-loss-1.0695", use_gpu=False)

test_data['source_text'][25001]

# predict
model.predict(test_data['source_text'][25001])

test_data['target_text'][25001]

#printing the first 10 predictions on test dataset
for i in range(25001,25010):
    print("news:",test_data['source_text'][i])
    print("original summary:",test_data['target_text'][i])
    print("predicted summary:",model.predict(test_data['source_text'][i]))
    print("\n")

import nltk
nltk.download('wordnet')

#calculating BlueScore for the Test dataset
#Test dataset range is 25001 to 26001 so N is 1000
from nltk.translate.bleu_score import sentence_bleu
def calculate_scores(N=1000):    
    bscore=0
    for i in range(25001,26001):
        ref=test_data['target_text'][i]
        hypo=str(model.predict(test_data['source_text'][i]))
        bscore+=sentence_bleu([ref],hypo,weights=(1,0,0,0))
    print("BLEU:%.4f "%(bscore/1000))

calculate_scores()