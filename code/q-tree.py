from pymystem3 import Mystem
from string import digits, punctuation
from index import preprocess_text
import nltk
import numpy as np
from varbyte import Varbyte_
from simple9 import Simple9_
import sys
import pickle
"""
[START] : python3 q-tree.py {0 : without showing tree, only len(ans) and ans, 1 : show tree, beauty ans} decoder {simple9, varbyte}


I try to build some kind of balanced tree,
all based on idea, that we good at building trees, 
which have 2**height words(all words is leafs)

query is smth kinda : a & b & (c || f & g & (k || l)) & d & e
    a. split by & at zero lvl of brackets(no brackets)          -> [a, b, (c || f & g & (k || l)), d, e]
    b. build tree using 2**n elems if brackets in element,
       recursive build tree                                     -> [[a, b, (c || [f, g, (k || l)], d], e]
    c. repeat it with left elements (left "e" element)
"""

class Node_leaf(object):
    def __init__(self, word, docs_data, parent=None):
        self.docs_data = docs_data
        self.size = len(docs_data)
        self.word = word
        self.ind = 0
        self.leaf = True
    
    def step(self):
        self.ind += 1
        if self.ind - 1 < self.size:
            return self.docs_data[self.ind - 1]
        return -1
    
    def next(self):
        if self.ind < self.size:
            return self.docs_data[self.ind]
        return -1


class Node_(object):
    def __init__(self, status="&", childs=[], parent=None, leaf=False):
        self.childs = childs
        self.parent = parent
        self.none_intersaction = 0
        self.queue = []
        self.status = status
        self.height = 0
        self.leaf = leaf
    
    def __str__(self):
        # if self.leaf:
        if self.status == "||":
            return self.status + ": [" +" ".join([i.word if isinstance(i, Node_leaf) else i.status for i in self.childs]) + "] "
        return self.status + " : [" +" ".join([i.word if isinstance(i, Node_leaf) else i.status for i in self.childs]) + "] "
        
        # else:
        #     return self.status

    def binary_search(self, list_num, first_index, last_index, to_search):
        if last_index >= first_index:
        
            mid_index = (first_index + last_index) // 2
            mid_element = list_num[mid_index]
        
    
            if mid_element == to_search:
                return 1
    
            elif mid_element > to_search:
                new_position = mid_index - 1
                return self.binary_search(list_num, first_index, new_position, to_search)
    
            elif mid_element < to_search:
                new_position = mid_index + 1
                return self.binary_search(list_num, new_position, last_index, to_search)
    
        else:
            return 0

    def step(self):
        if len(self.childs) == 1:
                self.childs[0].ind += 1
                if self.childs[0].ind - 1 < self.childs[0].size:
                    return self.childs[0].docs_data[self.childs[0].ind - 1]
                else:
                    return -1

        if self.status == "&":
            if isinstance(self.childs[0], Node_leaf) and isinstance(self.childs[1], Node_leaf):
                if self.childs[0].size > self.childs[1].size:
                    low_sz = self.childs[1]
                    high_sz = self.childs[0]
                else:
                    low_sz = self.childs[0]
                    high_sz = self.childs[1]

                cur_doc = low_sz.step()        
                while cur_doc != -1 and not self.binary_search(high_sz.docs_data, 0, high_sz.size - 1, cur_doc):
                    cur_doc = low_sz.step()
                return cur_doc
            else:
                left_doc = self.childs[0].step()
                right_doc = self.childs[1].step()
                while left_doc != -1 and right_doc != -1 and left_doc != right_doc:
                    if left_doc < right_doc:
                        left_doc = self.childs[0].step()
                    else:
                        right_doc = self.childs[1].step()
                return left_doc if left_doc != -1 and right_doc != -1 and left_doc == right_doc else -1


        if self.status == "||":
            if isinstance(self.childs[0], Node_leaf) and isinstance(self.childs[1], Node_leaf):
                if self.childs[0].next() < self.childs[1].next():
                    return self.childs[0].step()
                return self.childs[1].step()
            else:
                if self.queue:
                    return self.queue.pop()
                left_doc = self.childs[0].step()
                right_doc = self.childs[1].step()
                if left_doc == -1 and right_doc == -1 : return -1
                if left_doc == -1 : return right_doc
                if right_doc == -1 : return left_doc
                if left_doc < right_doc:
                    self.queue.insert(0, right_doc)
                    return left_doc
                self.queue.insert(0, left_doc)
                return right_doc

    def add_child(self, child):
        assert len(self.childs) < 2
        self.childs.append(child)


class Q_tree_(object):
    def __init__(self, query, decoder=Simple9_()):
        # print("[QUERY] :", query)
        self.decoder = decoder
        self.string_query = query
        self.query = self.splitter_and(query)
        self.root = None
        self.cur_ind = 0
        self.back_index_path = '../data/index_data/back_index_bin'
        self.back_index_info_path = '../data/index_data/back_index_info'
        self.word_id_path = "../data/index_data/termId_term"
        self.doc_id_url_path = "../data/index_data/docId_url"

        with open(self.back_index_path, 'rb') as f1, \
             open(self.back_index_info_path, 'rb') as f4, \
             open(self.word_id_path, 'rb') as f2, \
             open(self.doc_id_url_path, 'rb') as f3:

            self.back_index = f1.read().split(bytes('~®', 'utf-8'))
            self.back_index_info = pickle.load(f4)
            self.word_id = pickle.load(f2)
            self.doc_id_url = pickle.load(f3)

    def build_twoPow(self, height):
        # print("[HEIGHT] :", height)
        finish = self.cur_ind + 2**height
        # print(self.query)
        if height == 0:
            # print("[SINGLE]")
            cur_word = self.query[self.cur_ind]
            self.cur_ind+=1
            if cur_word[0] != '(':
                cur_docs = self.decoder.decode_list(self.back_index[self.back_index_info[self.word_id[cur_word]]])
                return Node_(childs=[Node_leaf(cur_word, cur_docs)], leaf=True)
            else:
                return self.process_or(cur_word[1:-1])

        root = Node_()
        queue = [root]
        while queue:
            # print("[LEN QUEUE] :", len(queue), self.cur_ind, len(self.query))
            cur = queue.pop()
            if isinstance(cur, Node_leaf):
                continue
            if self.cur_ind == finish: # beacuse ||
                # print("[BREAK]")
                break
            if cur.height + 1 == height:
                # print(len(self.query), self.cur_ind)
                cur_word_left = self.query[self.cur_ind]
                cur_word_right = self.query[self.cur_ind + 1]
                # print(cur_word_left, "***", cur_word_right)
                flag = 0
                self.cur_ind += 2
                if cur_word_left[0] != '(':
                    left_docs = self.decoder.decode_list(self.back_index[self.back_index_info[self.word_id[cur_word_left]]])
                    node_left = Node_leaf(cur_word_left, left_docs)
                    flag += 1
                else:
                    node_left = self.process_or(cur_word_left[1:-1])
                    # print("**")
                    self.increase_height(node_left, cur.height + 1)
                    # print("**")

                if cur_word_right[0] != '(':
                    right_docs = self.decoder.decode_list(self.back_index[self.back_index_info[self.word_id[cur_word_right]]])
                    node_right = Node_leaf(cur_word_right, right_docs)
                    flag += 1
                else:
                    node_right = self.process_or(cur_word_right[1:-1])
                    # print("***")
                    self.increase_height(node_right, cur.height + 1)
                    # print("***")
                
                cur.childs = [node_left, node_right]
                if flag == 2 : cur.leaf = True
                if flag == 1 :queue.insert(0, node_right)
                if flag == 2: queue.insert(0, node_left)
            else:
                left_child = Node_(parent=cur)
                right_child = Node_(parent=cur)
                left_child.height = cur.height + 1
                right_child.height = cur.height + 1
                cur.childs = [left_child, right_child]
                queue.insert(0, right_child)
                queue.insert(0, left_child)
        return root

    def increase_height(self, node, num=1):
        queue = [node]
        while queue:
            cur = queue.pop()
            cur.height += num
            for child in cur.childs:
                if isinstance(child, Node_):
                    queue.insert(0, child)

    def build(self):
        n_words = len(self.query[self.cur_ind:])
        cur_height = int(np.log2(n_words))
        self.root = self.build_twoPow(cur_height)
        # print(self.cur_ind, len(self.query))
        # print('-'*10)
        while self.cur_ind != len(self.query):
            # print("[WORDS LAST] : ", self.query[self.cur_ind:])
            # print(self.cur_ind, len(self.query))
            n_words = len(self.query[self.cur_ind:])
            cur = self.build_twoPow(int(np.log2(n_words)))
            compare = Node_(childs=[self.root, cur])
            self.increase_height(self.root)
            self.increase_height(cur)
            self.root.parent = compare
            cur.parent = compare
            self.root = compare
                
    def step(self, id_=False, print_=True, beuty=False):
        if beuty:
            print('-'*29 + "[RESULT]" + "-"*29)
        ans = []
        cur = self.root.step()
        while -1 != cur:
            ans.append(cur)
            cur = self.root.step()
        if not id_:
            ans = [self.doc_id_url[i] for i in sorted(ans) if i in self.doc_id_url]

        if not print_:
            return ans
        print(len(ans))
        print(*ans, sep='\n')
        if beuty:
            print('-'*27 + "[RESULT END]" + "-"*27)
    
    def show(self):
        print(30*'-' + '[SHOW]' + 30*'-')
        print("[QUERY] :" + self.string_query + '\n')
        print("[HEIGHT]\t[STATUS : [CONTENT]]")
        queue = [self.root]
        cnt = 1
        while queue:
            cur = queue.pop()
            print('*'*(cur.height+1) + '\t\t', cur)
            cnt+=1
            for child in cur.childs:
                if isinstance(child, Node_):
                    queue.insert(0, child)
        print(28*'-' + '[SHOW END]' + 28*'-')

    def splitter_and(self, query):
        if query[-1] != ')' : query += " &"
        cnt, last = 0, 0
        ans = []
        for ind, ch in enumerate(query):
            if ch == '&' and cnt == 0 and last < ind:
                ans.append(query[last:ind - 1])
                last = ind + 2
            if ch == '(':
                if cnt == 0:
                    last = ind
                cnt+=1
            if ch == ')':
                cnt-=1
                if cnt == 0:
                    ans.append(query[last:ind+1])
                    if ind + 4 < len(query):
                        last = ind + 4
        return ans

    def splitter_or(self, query):
        ans = []
        cnt = 0
        for ind, ch in enumerate(query):
            if ch == "(" : cnt += 1
            if ch == ")" : cnt -= 1
            if ch == "|" and cnt == 0:
                ans.append(query[:ind - 1])
                ans.append(query[ind+3:])
                break
        return ans

    def process_or(self, query):
        words = self.splitter_or(query)
        # print(query)
        assert len(words) == 2
        flag = 0
        if words[0][0] != '(':
            # left_docs = self.decoder.decode_list(self.back_index[self.back_index_info[self.word_id[words[0]]]])
            # left_node = Node_leaf(words[0], left_docs)
            tree = Q_tree_(words[0], decoder=self.decoder)
            tree.build()
            if len(tree.root.childs) == 2:
                left_node = tree.root
                self.increase_height(left_node)
            else:
                left_node = tree.root.childs[0]
            flag+=1
        else:
            # print("---")
            left_node = self.process_or(words[0][1:-1])
            self.increase_height(left_node)
        
        if words[1][0] != '(':
            # right_docs = self.decoder.decode_list(self.back_index[self.back_index_info[self.word_id[words[1]]]])
            # right_node = Node_leaf(words[1], right_docs)
            tree = Q_tree_(words[1], decoder=self.decoder)
            tree.build()
            if len(tree.root.childs) == 2:
                right_node = tree.root
                self.increase_height(right_node)
            else:
                right_node = tree.root.childs[0]
            flag+=1
        else:
            # print("---")
            right_node = self.process_or(words[1][1:-1])
            self.increase_height(right_node)
        
        ans = Node_(status = '||',childs=[left_node, right_node])
        if flag == 2: ans.leaf = True
        return ans

if __name__ == "__main__":
    beuty = sys.argv[-1]
    beuty = int(beuty)
    with open("../code/user_data/decoder.txt", 'r') as f:
        deco = f.read().strip()

    assert deco in {"varbyte", "simple9"}, "[DECODER ERROR] : decoder must be one of [varbyte, simple9]"
    deco_dict = {"varbyte" : Varbyte_(), "simple9" : Simple9_()}
    decoder = deco_dict[deco]

    # query_0   = "(путин || россия & истина) & правда"
    # query_1   = "((путин || правда) || (луна || небо)) & истина"
    # query_and = "россия & запуск & ((слава || вечер) || (луна || вечер)) & солнце & вечер & (четыре || пять) & семь"
    # query_or  = "север & ((слава || вечер & поезд & (путин || россия) & восемь) || вечер)"

    with open("../code/user_data/query.txt", 'r') as f:
        query = f.read().strip('\n')

    tree = Q_tree_(query, decoder=decoder)
    tree.build()
    if beuty:
        tree.show()
    tree.step(beuty=beuty)