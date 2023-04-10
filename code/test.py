from varbyte import Varbyte_
from simple9 import Simple9_
import pickle
import sys
import unittest

class tests(unittest.TestCase):

    decoder = "simple9"
    
    def test_varbyte(self):
        vb = Varbyte_()
        self.assertEqual(b'\x01\xbf', vb.encode_single(191))
        self.assertEqual(b'\x83', vb.encode_single(3))
        self.assertEqual(vb.decode_single(vb.encode_single(123548612)), 123548612)
        self.assertEqual(vb.decode_list(vb.encode_list([3, 2, 3, 191])), [3, 2, 3, 191])
        self.assertEqual(vb.decode_list(vb.encode_list([9600, 9646])), [9600, 9646])
    
    def test_simple9(self):
        sp = Simple9_()
        self.assertEqual(sp.decode_pack(sp.encode_pack(7, [77,11,129])), [77,11,129])
        self.assertEqual(sp.decode_list(sp.encode_list([3, 2, 3, 191])), [3, 2, 3, 191])
        self.assertEqual(sp.decode_list(sp.encode_list([9600, 9646])), [9600, 9646])

    def test_dict(self,
                  path_bin_ind = '../data/index_data/back_index_bin',
                  data_path = '../data/index_data/back_index',
                  back_index_info_path = '../data/index_data/back_index_info',
                  termid_term_path = '../data/index_data/termId_term'):

        dec = 0
        if self.decoder == "varbyte":
            dec = Varbyte_()
        elif self.decoder == "simple9":
            dec = Simple9_()
        assert dec, "[BAD DECODER] : try one of ['varbyte', 'simple9']"

        with open(back_index_info_path, 'rb') as f1, open(data_path, 'rb') as f2:
            back_indeces = pickle.load(f1)
            back_index = pickle.load(f2)

        with open(path_bin_ind, 'rb') as f:
            text = f.read().split(bytes('~®', 'utf-8'))
            for word_id in back_indeces:
                ind = back_indeces[word_id]
                data = text[ind]
                docs = dec.decode_list(data)
                assert docs == back_index[word_id], f"[{word_id}] : docs mismatch, {len(docs), len(list(back_index[word_id]))}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        tests.decoder = sys.argv.pop()
    unittest.main()