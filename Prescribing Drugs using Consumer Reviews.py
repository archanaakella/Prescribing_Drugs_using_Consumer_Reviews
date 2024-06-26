#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install numpy


# In[2]:


pip install pandas


# In[3]:


pip install matplotlib


# In[4]:


import numpy as np
import pandas as pd
import string

import matplotlib.pyplot as plt
import seaborn as sns

import ipywidgets
from ipywidgets import interact

plt.rcParams['figure.figsize'] = (15, 5)
plt.style.use('fivethirtyeight')


# In[5]:


# reading the Dataset
data = pd.read_csv('drug.csv')

# lets print the shape of the dataset
print("The Shape of the Dataset :", data.shape)


# In[6]:


# lets check the head of the dataset
data.head()


# In[7]:


# lets Explore Some of the Important Column in the dataset

print("Number of Unique Drugs present in the Dataset :", data['drugName'].nunique())
print("Number of Unique Medical Conditions present in the Dataset :", data['condition'].nunique())

print("\nThe Time Period of Collecting the Data")
print("Starting Date :", data['date'].min())
print("Ending Date :", data['date'].max())


# In[8]:


# lets summarize the Dataset
data[['rating','usefulCount']].describe()


# In[9]:


# lets check the Number and Name of the Drugs with 0 Useful Count in Details
print("Analysis on Useless Drugs")
print("----------------------------")
print("The Number of Drugs with No Useful Count :", data[data['usefulCount'] == 0].count()[0])

# Lets Check the Number of Drugs with No Usesful Count with Review Greater than or Equal to 8
print("Number of Good Drugs with Lesser Useful Count :", data[(data['usefulCount'] == 0) &
                                                data['rating'] >= 8].count()[0])

# Lets Check the Average Rating of the Drugs with No Useful Count
print("Average Rating of Drugs with No Useful Count : {0:.2f}".format(data[data['usefulCount'] == 0]['rating'].mean()))

print("\nAnalysis on Useful Drugs")
print("----------------------------")
print("The Number of Drugs with Greater than 1000 Useful Counts :", data[data['usefulCount'] > 1000].count()[0])
print("Average Rating of Drugs with 1000+ Useful Counts :", data[data['usefulCount'] > 1000]['rating'].mean())
print("\nName and Condition of these Drugs: \n\n", 
    data[data['usefulCount'] > 1000][['drugName','condition']].reset_index(drop = True))


# In[10]:


# lets summarize Categorical data also
data[['drugName','condition','review']].describe(include = 'object')


# In[11]:


# lets check for Missing Values
data.isnull().sum()


# In[12]:


# as we know that condition is an Important Column, so we will delete all the records where Condition is Missing
data = data.dropna()

# lets check the Missing values now
data.isnull().sum().sum()


# In[13]:


# lets check the Distribution of Rating and Useful Count

plt.rcParams['figure.figsize'] = (15, 4)

plt.subplot(1, 2, 1)
sns.distplot(data['rating'])

plt.subplot(1, 2, 2)
sns.distplot(data['usefulCount'])

plt.suptitle('Distribution of Rating and Useful Count \n ', fontsize = 20)
plt.show()


# In[14]:


import matplotlib.pyplot as plt
import seaborn as sns

# Set figure size
plt.rcParams['figure.figsize'] = (15, 4)

# Create bar plot with x and y as keyword arguments
sns.barplot(x='rating', y='usefulCount', data=data, palette='hot')

# Add grid, labels, and title
plt.grid()
plt.xlabel('\n Ratings')
plt.ylabel('Count\n', fontsize=20)
plt.title('\n Rating vs Usefulness \n', fontsize=20)

# Show the plot
plt.show()


# In[15]:


# for that we need to create a new column to calculate length of the reviews
data['len']  = data['review'].apply(len)


# In[16]:


# lets check the Impact of Length of Reviews on Ratings
data[['rating','len']].groupby(['rating']).agg(['min','mean','max'])


# In[17]:


# lets check the Highest Length Review
print("Length of Longest Review", data['len'].max())
data['review'][data['len'] == data['len'].max()].iloc[0]


# In[18]:


# as it is clear that the reviews have so many unnecassry things such as Stopwords, Punctuations, numbers etc

# First lets remove Punctuations from the Reviews
def punctuation_removal(messy_str):
    clean_list = [char for char in messy_str if char not in string.punctuation]
    clean_str = ''.join(clean_list)
    return clean_str

data['review'] = data['review'].apply(punctuation_removal)


# In[19]:


import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download the stopwords dataset
nltk.download('stopwords')
nltk.download('punkt')

stop = stopwords.words('english')
stop.append("i'm")

stop_words = []

def punctuation_removal(text):
    import string
    return text.translate(str.maketrans('', '', string.punctuation))

for item in stop:
    new_item = punctuation_removal(item)
    stop_words.append(new_item)

def stopwords_removal(messy_str):
    messy_str = word_tokenize(messy_str)
    return [word.lower() for word in messy_str if word.lower() not in stop_words]

# Assuming 'data' is a pandas DataFrame and 'review' is a column in it
data['review'] = data['review'].apply(stopwords_removal)


# In[20]:


# lets remove the Numbers also

import re
def drop_numbers(list_text):
    list_text_new = []
    for i in list_text:
        if not re.search('\d', i):
            list_text_new.append(i)
    return ' '.join(list_text_new)

data['review'] = data['review'].apply(drop_numbers)


# In[21]:


# for using Sentiment Analyzer we will have to dowload the Vader Lexicon from NLTK

import nltk
nltk.download('vader_lexicon')


# In[22]:


# lets calculate the Sentiment from Reviews

from nltk.sentiment.vader import SentimentIntensityAnalyzer
sid = SentimentIntensityAnalyzer()

train_sentiments = []

for i in data['review']:
    train_sentiments.append(sid.polarity_scores(i).get('compound'))
    
train_sentiments = np.asarray(train_sentiments)
data['sentiment'] = pd.Series(data=train_sentiments)


# In[23]:


# lets check Impact of Sentiment on Reviews
data[['rating','sentiment']].groupby(['rating']).agg(['min','mean','max'])


# In[24]:


# as we can see that Sentiment and length of the review are not related to Reviews, we will drop the sentiment column

# lets remove the unique Id, date, review, len, and sentiment column also
data = data.drop(['date','uniqueID','sentiment','review','len'], axis = 1)

# lets check the name of columns now
data.columns


# In[11]:


# Lets Calculate an Effective Rating


min_rating = data['rating'].min()
max_rating = data['rating'].max()

def scale_rating(rating):
    rating -= min_rating
    rating = rating/(max_rating -1)
    rating *= 5
    rating = int(round(rating,0))
    
    if(int(rating) == 0 or int(rating)==1 or int(rating)==2):
        return 0
    else:
        return 1
    
data['eff_score'] = data['rating'].apply(scale_rating)


# In[12]:


# lets also calculate Usefulness Score

data['usefulness'] = data['rating']*data['usefulCount']*data['eff_score']

# lets check the Top 10 Most Useful Drugs with their Respective Conditions
data[['drugName','condition','usefulness']][data['usefulness'] > 
                            data['usefulness'].mean()].sort_values(by = 'usefulness', 
                                        ascending = False).head(10).reset_index(drop = True)


# In[17]:


import pandas as pd
import ipywidgets as widgets
from ipywidgets import interact

# Load your data into the 'data' variable
data = pd.read_csv(r"C:\Users\archa\OneDrive\Documents\projectDPCR\drug.csv")

# Display column names to verify
print("Column names in the DataFrame:", data.columns)

# Compute the eff_score if needed (example: eff_score = rating * usefulCount)
data['eff_score'] = data['rating'] * data['usefulCount']

# Update interact function based on verified column names
@interact
def check(condition=list(data['condition'].value_counts().index)):
    return data[data['condition'] == condition]['eff_score'].value_counts()


# In[21]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load your data into the 'data' variable
data = pd.read_csv(r"C:\Users\archa\OneDrive\Documents\projectDPCR\drug.csv")

# Compute the eff_score if needed (example: eff_score = rating * usefulCount)
data['eff_score'] = data['rating'] * data['usefulCount']

# Define popular conditions
popular_conditions = ('Birth Control', 'Depression', 'Pain', 'Anxiety', 'Acne', 
                      'Bipolar Disorder', 'Insomnia', 'Weight Loss', 'Obesity', 
                      'ADHD', 'Diabetes, Type 2', 'Emergency Contraception', 
                      'High Blood Pressure', 'Migraine')

# Filter data for popular conditions
conditions = data.loc[data['condition'].isin(popular_conditions)]

# Create a bar plot showing the average rating for each condition
plt.figure(figsize=(12, 6))
sns.barplot(x='condition', y='rating', data=conditions, palette='autumn')
plt.title('Conditions vs Average Rating of Drugs')
plt.xticks(rotation=90)
plt.ylabel('Average Rating')
plt.xlabel('Condition')
plt.show()


# In[22]:


# lets check the Most Common Conditions

print("Number of Unique Conditions :", data['condition'].nunique())
data['condition'].value_counts().head(10)


# In[23]:


# lets check Drugs, which were useful to Highest Number of Poeple
data[['drugName','usefulCount']][data['usefulCount'] >
                    data['usefulCount'].mean()].sort_values(by = 'usefulCount',
                                        ascending = False).head(10).reset_index(drop = True)


# In[24]:


# lets remove all the Duplicates from the Dataset
data = data.drop_duplicates()


# In[27]:


import pandas as pd
import ipywidgets as widgets
from ipywidgets import interact

# Load your data into the 'data' variable
data = pd.read_csv(r"C:\Users\archa\OneDrive\Documents\projectDPCR\drug.csv")

# Display column names to verify
print("Column names in the DataFrame:", data.columns)

# Update interact function based on verified column names
@interact
def high_low_rate(condition=list(data['condition'].value_counts().index)):
    print("\n Top 5 Drugs")
    print(data[data['condition'] == condition][['drugName', 'usefulCount']].sort_values(by=['usefulCount'],
                                                  ascending=False).head().reset_index(drop=True))
    print("\n\n Bottom 5 Drugs")
    print(data[data['condition'] == condition][['drugName', 'usefulCount']].sort_values(by=['usefulCount'],
                                                  ascending=True).head().reset_index(drop=True))


# In[ ]:




