import os
from string import digits, punctuation
from collections import defaultdict
import pickle
import nltk
from nltk.corpus import stopwords
from tqdm import tqdm
from pymystem3 import Mystem
path_read = "../data/dataset/"
path_docid_url = "../data/index_data/docId_url"
path_termid_term = "../data/index_data/termId_term"
path_back_index = "../data/index_data/back_index"

nltk.download("stopwords", quiet=True)


mystem = Mystem() 
russian_stopwords = stopwords.words("russian")
remove_digits = str.maketrans('', '', digits + punctuation)

def preprocess_text(text, mystem=mystem):
    tokens = mystem.lemmatize(text.lower())
    tokens = [token.translate(remove_digits) for token in tokens if token not in russian_stopwords\
              and token != " " \
              and token.strip() not in punctuation \
              and len(token.translate(remove_digits)) > 2]
    
    return tokens

if __name__ == '__main__':

    d = defaultdict(set)
    cur_id, cur_word_id, cur_text = 0, 0, ""
    back_index, bag_of_words, bag_of_urls = {}, {}, {}
    remove_digits = str.maketrans('', '', digits + punctuation + '«»')
    for i in tqdm(range(len(os.listdir(path_read)))):
        with  open(path_read + os.listdir(path_read)[i], 'rb') as f:
            for line in f:
                decode_line = line.decode(errors='replace')
                if decode_line[1:5] == 'http':
                    url = decode_line[1:decode_line.rfind('/')]
                    if cur_id :
                        cur_text = preprocess_text(cur_text)
                        for word in cur_text:
                            if word not in bag_of_words:
                                cur_word_id+=1
                                bag_of_words[word] = cur_word_id
                            d[bag_of_words[word]].add(cur_id)
                            

                    cur_id += 1
                    bag_of_urls[cur_id] = url
                    cur_text = ""
                    continue
                
                if cur_id: cur_text += decode_line

    for word in d:
        d[word] = sorted(list(d[word]))
        # print(d[word])

    with open(path_back_index, 'wb') as f1, open(path_docid_url, 'wb') as f2, open(path_termid_term, 'wb') as f3:
        pickle.dump(dict(d), f1)
        pickle.dump(bag_of_urls, f2) #id -> url
        pickle.dump(bag_of_words, f3) #word -> id