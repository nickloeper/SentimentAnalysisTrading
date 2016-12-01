import sys,pandas,nltk,re,math,time, tqdm
from nltk.tokenize import TweetTokenizer
from nltk.tokenize import MWETokenizer
from nltk.corpus import stopwords
import numpy as np
import _pickle as pc

STOCKS = ['aapl','goog','amzn','msft']
SYMBOLS = ['@','#','$','.',',',':', '…','...','(',')','"','[',']']
REMOVABLES = ['rt'] #'the', 'my','i','we','me','you']
STOPWORDS = set(stopwords.words('english'))
EMOTICONS = [(':)','smile'), ('(:','smile'), ('):','frown'), (':(','frown'), (':D','biggrin'), (':\'(','crying'), (':\'‑(','crying'), (')\':','crying'), (')-\':','crying'), ('D:','sadness'), (':O','surprise'), (':o','shock') ]


def preprocess(pdata):
    print('Preprocessing...')
    
    dataframe = pandas.read_pickle(pdata) #get pickled dataset from location passed in as a parameter to the function
    preprocessed_dataframe = pandas.DataFrame(columns=['date','text','retweets','favorites','followers']).set_index('date')
    
    ##ITERATE THROUGH EVERY TWEET IN THE DATAFRAME
    for it, tweet in tqdm.tqdm(dataframe.iterrows()):
        
        text = tweet[0]
        retweets = tweet[1]
        favorites = tweet[2]
        followers = tweet[3]
        date = it
        
        ##if either retweets, favorites, or followers is NaN, replace NaN with 0
        if(math.isnan(retweets)):
            retweets = 0
        if(math.isnan(favorites)):
            favorites = 0
        if(math.isnan(followers)):
            followers = 0
            
        #text = text+':) :( :) :(' #TEST for emoticon replacement
        #text = text+"gooooood, jeeeeezz" #TEST for repeated letter reduction
        
        text = text.replace('#','') #remove hashes
        text = text.replace('%', 'percent') #replace % symbol with 'percent'
        
        ##Iterate though listed emoticons and their corrisponding emotions, replace symbol with emotion word
        for symbol, emotion  in EMOTICONS:
            text = text.replace(symbol, emotion)
            
        text =  re.sub(r"http\S+", "", text) #remove URLs from Tweet text
        #text = re.sub(r'([a-zA-Z])\1{3,}', r'\1\1\1', text) #reduce excessively long repeated letters ##REPLACED BY TweetTokenizer built-in function
        tk = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True) #create new TweetTokenizer, take all text to lowercase and remove users handles from Tweet text
        tk2 = MWETokenizer()
        
        tokenizedtext = tk.tokenize(text) #tokenize the Tweet text using TweetTokenizer
        tokenizedtext = tk2.tokenize(tokenizedtext)
        tokenizedtext = [word for word in tokenizedtext if (word not in STOPWORDS and word not in SYMBOLS and word not in STOCKS and word not in REMOVABLES)] #remove stopwords, extra symbols, target stocks, and other removable phrases
        
        temp = pandas.DataFrame({
            'date':date,
            'text':[tokenizedtext],
            'retweets':retweets,
            'favorites':favorites,
            'followers':followers
        }, columns=['date','text','retweets','favorites','followers']).set_index('date')
        preprocessed_dataframe = preprocessed_dataframe.append(temp)
        
    #print(preprocessed_dataframe) #printout of the preprocessed dataframe
    preprocessed_dataframe.to_pickle('preprocessed_tweets_s'+str(int(len(dataframe)/100))+'.p') #create a pickled dataframe with a semi-unique identifier (based on the number of rows in the dataframe)
    return preprocessed_dataframe #return the dataframe
    
preprocess(str(sys.argv[1]))