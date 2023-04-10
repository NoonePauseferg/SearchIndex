import array
from varbyte import Varbyte_

class Simple9_(object):
    """
    - do the next 28 numbers fit into 1 bit each?
        - No? do the next 14 numbers fit 2 one bit each?
            - No? ...
    """
    def __init__(self):
        self.bytes_per_word = {
           #code   n_bytes    max      n_num
            1   :   [1,        1,        28],
            2   :   [2,        3,        14],
            3   :   [3,        7,         9],
            4   :   [4,        15,        7],
            5   :   [5,        31,        5],
            6   :   [7,        127,       4],
            7   :   [9,        511,       3],
            8   :   [14,       16383,     2],
            9   :   [28,       268435455, 1]
        }

    def encode_pack(self, code, nums):
        ans = code << 28
        bytes_ans = array.array('B')
        n_bytes, ma, num = self.bytes_per_word[code]
        for ind, num in enumerate(nums):
            ans = ans | num << (n_bytes * ind)
        for i in range(4):
            bytes_ans.append((ans >> (i * 8)) & 255)
        assert len(bytes_ans) == 4
        return bytes_ans[::-1].tobytes()

    def decode_pack(self, pack : bytes):
        assert len(pack) == 4
        big_num = int.from_bytes(pack, 'big')
        code = big_num >> 28
        assert code in self.bytes_per_word, f"[BAD ENCODING] : {pack}"
        ans = []
        n_bytes, ma, num = self.bytes_per_word[code]
        for i in range(num):
            cur = (big_num & ma << n_bytes*i) >> n_bytes*i
            ans.append(cur)
        ind = len(ans) - 1
        while ans[ind] == 0:
            ind -= 1
        return ans[:ind+1]

    def encode_list(self, nums : list) -> bytes:
        ind = 0
        ans = b''
        while ind < len(nums):
            for code, (bts, cur_max, num) in self.bytes_per_word.items():
                cur_list = nums[ind:ind + num]
                if max(cur_list) <= cur_max:
                    ans += self.encode_pack(code, cur_list)
                    ind += num
                    break
        return ans

    def decode_list(self, nums : bytes) -> list:
        ans = []
        for i in range(0, len(nums), 4):
            cur_bytes = nums[i:i+4]
            if len(cur_bytes) == 4:
                ans += self.decode_pack(cur_bytes)
        return ans