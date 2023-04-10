import array

class Varbyte_(object):
    def __init__(self):
        pass

    def encode_single(self, num : int) -> array.array:
        array_single = array.array('B')
        while num > 0:
            array_single.append(num % 0x80)
            num = num // 0x80
        array_single[0] += 0x80
        return array_single[::-1].tobytes()

    def decode_single(self, num : bytes) -> int:
        # a-> a//0x80 (a%0x80 + 0x80) -> a//0x80//0x80 a//0x80%0x80 (a%0x80 + 0x80) 
        bytes_array_single = array.array('B')
        bytes_array_single.frombytes(num)
        ans = 0
        for ind, byte_ in enumerate(bytes_array_single[::-1]):
            if ind == 0:
                ans += byte_ - 0x80
            else:
                ans += byte_* 0x80**ind
        return ans

    def encode_list(self, nums : list) -> bytes:
        bytes_str = b''
        for num in nums:
            bytes_str += self.encode_single(num)
        return bytes_str

    def decode_list(self, nums : bytes) -> list:
        ans, start, end = [], 0, 0
        for ind, i in enumerate(nums):
            if i >= 0x80:
                ans.append(self.decode_single(nums[start:ind+1]))
                start = ind + 1
        return ans