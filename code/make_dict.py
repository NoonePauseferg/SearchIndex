import pickle
from collections import defaultdict
import sys
from varbyte import Varbyte_
from simple9 import Simple9_

"""
1 binary file with data
2 binary file : word_id, start_ptr(docks), end_ptr(start_freq), end_freq
"""

def make_dict(data_path = '../data/index_data/back_index',
              compressed_data_path = '../data/index_data/back_index_bin',
              back_index_info_path = '../data/index_data/back_index_info', \
              decoder=Varbyte_()):
    vb = decoder
    index_info = {}

    with open(compressed_data_path, 'wb') as f1, \
         open(data_path, 'rb') as f2, \
         open(back_index_info_path, 'wb') as f3:
         
        back_index = pickle.load(f2)
        for ind, word_id in enumerate(back_index):
            docs_bytes = vb.encode_list(back_index[word_id])
            index_info[word_id] = ind
            f1.write(docs_bytes)
            f1.write(bytes('~®', 'utf-8'))
        pickle.dump(index_info, f3)
        
    # DEBUG
    # with open(compressed_data_path, 'rb') as f1:
    #     data = f1.read().split(bytes('~®', 'utf-8'))
    #     for ind, l_l in index_info.values():
    #         cur_bytes = data[ind]
    #         cur_docs = vb.decode_list(cur_bytes[:l_l])
    #         assert len(cur_docs) == len(cur_freqs), f"{cur_docs} : {cur_freqs}; {l_l}, {f_l}, {len(cur_bytes)}"

if __name__ == "__main__":
    d = sys.argv[-1]
    decoder = 0
    if d == "varbyte":
        decoder = Varbyte_()
    elif d == "simple9":
        decoder = Simple9_()
    assert decoder, "[BAD DECODER] : try one of ['varbyte', 'simple9']"
    make_dict(decoder = decoder)
