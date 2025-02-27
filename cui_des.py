def _add_padding(message):
    """Adds padding to the message to ensure it's a multiple of 8 bytes."""
    # AI generated
    pad_len = 8 - (len(message) % 8)
    return message + bytes([pad_len] * pad_len)

def _rem_padding(message):
    """Removes padding from the message."""
    # AI generated
    pad_len = message[-1]
    return message[:-pad_len]

def _bytes_to_bit_array(byte_string):
    """Converts bytes to a list of bits."""
    # AI generated
    bit_array = []
    for byte in byte_string:
        bits = bin(byte)[2:].rjust(8, '0')
        bit_array.extend([int(bit) for bit in bits])
    return bit_array

def _bit_array_to_bytes(bit_array):
    """Converts a list of bits back to bytes."""
    # AI generated
    byte_string = bytearray()
    for i in range(0, len(bit_array), 8):
        byte = bit_array[i:i+8]
        byte_string.append(int(''.join([str(bit) for bit in byte]), 2))
    return bytes(byte_string)

def _nsplit(data, split_size=64):
    """Splits data into chunks of a given size."""
    # AI generated
    return [data[i:i+split_size] for i in range(0, len(data), split_size)]

def _hex_print(msg, block, length=16):
    """Prints a hexadecimal representation of a data block."""
    # AI generated
    hex_str = ''.join([f"{byte:02x}" for byte in block[:length]])

def _permute(block: list, table: list):
    """Performs a permutation on the input block according to the given table."""
    # AI generated
    return [block[pos] for pos in table]

def _lshift(sequence: list, n: int):
    """Performs a left circular shift on the input list."""
    # AI generated
    return sequence[n:] + sequence[:n]

def _xor(x: list, y: list):
    """Performs a bitwise XOR between two bit lists."""
    # AI generated
    return [a ^ b for a, b in zip(x, y)]

def _generate_subkeys(encryption_key: bytes):
    """Generates sybkeys from the 64-bit encryption key"""
    # AI generated

    key_bits = _bytes_to_bit_array(encryption_key)

    permuted_key = _permute(key_bits, _KEY_PERMUTATION1)

    C, D = _nsplit(permuted_key, len(permuted_key) // 2)

    subkeys = []

    for i in range(16):
        C = _lshift(C, _KEY_SHIFT[i])
        D = _lshift(D, _KEY_SHIFT[i])
        
        combined_key = C + D
        
        subkey = _permute(combined_key, _KEY_PERMUTATION2)
        subkeys.append(subkey)
    
    return subkeys

def _substitute(expanded_block):
    """
    Substitutes the expanded block using the 8 DES S-boxes and then permutes the result.
    """
    # AI

    # Split the expanded 48-bit block into eight 6-bit chunks
    if len(expanded_block) != 48:
        raise ValueError("Bit array not 48")

    output = []
    tableNum = 0
    for i in range(0, len(expanded_block), 6):
        chunk = expanded_block[i:i+6]
        rowNum = int(f"{chunk[0]}{chunk[5]}",2)
        colNum = int(f"{chunk[1]}{chunk[2]}{chunk[3]}{chunk[4]}",2)
        sboxVal = SBOXES[tableNum][rowNum][colNum]
        binString = bin(sboxVal)[2:].zfill(4)
        binList = [int(bit) for bit in binString]
        output += binList
        tableNum += 1

    return output

def _func_f(R, subkey_i):
    tmp = _permute(R, _EXPAND)
    tmp = _xor(tmp, subkey_i)
    tmp = _substitute(tmp)
    tmp = _permute(tmp, _SBOX_PERM)
    return tmp

def _crypt_block(block, subkeys):
    block = _permute(block, PC1)
    L = block[:32]
    R = block[32:]

    for i in range(16):
        tmp = _func_f(R,subkeys[i])
        tmp = _xor(tmp, L)
        L = R
        R = tmp

    block = _permute(R+L, PC2)

    return block

class DES:
    def __init__(self, key, mode="ECB", iv=b'\x00\x00\x00\x00\x00\x00\x00\x00', pad=True):
        self.key = key
        self.mode = mode.upper()
        self.pad = pad

        self.iv = iv
        self._iv = _bytes_to_bit_array(iv)

    def encrypt(self, pt):
        """ Encrypts plaintext data with DES (Data Encryption Standard)."""

        subkeys = _generate_subkeys(self.key)

        if self.pad == True:
            if self.mode == "CBC" or self.mode=="ECB":
                pt = _add_padding(pt)
        pt = _bytes_to_bit_array(pt)

        result = []
    
        if self.mode == "CBC":
            for block in _nsplit(pt, 64):
                cblock = _xor(block, self._iv)
                cblock = _crypt_block(cblock, subkeys)
                self._iv = cblock
                result += cblock
            return _bit_array_to_bytes(result)

        elif self.mode == "OFB":
            for block in _nsplit(pt, 64):
                self._iv = _crypt_block(self._iv, subkeys)
                cblock = _xor(block, self._iv)
                result += cblock
            return _bit_array_to_bytes(result)

        else:
            for block in _nsplit(pt, 64):
                result += _crypt_block(block, subkeys)
            return _bit_array_to_bytes(result)
        

    def decrypt(self, ct):
        """ Decrypts plaintext data with DES (Data Encryption Standard)."""

        self.reset()

        subkeys = _generate_subkeys(self.key)
        if self.mode == "CBC" or self.mode == "ECB":
            subkeys.reverse()

        ct = _bytes_to_bit_array(ct)
        result = []

        if self.mode == "CBC":
            for block in _nsplit(ct, 64):
                cblock = _crypt_block(block, subkeys)
                cblock = _xor(cblock, self._iv)
                result += cblock
                self._iv = block
            result = _bit_array_to_bytes(result)
            return _rem_padding(result)

        elif self.mode == "OFB":
            for block in _nsplit(ct, 64):
                self._iv = _crypt_block(self._iv, subkeys)
                cblock = _xor(block, self._iv)
                result += cblock
            result = _bit_array_to_bytes(result)
            return result

        else:
            for block in _nsplit(ct, 64):
                result += _crypt_block(block, subkeys)
            result = _bit_array_to_bytes(result)
            return _rem_padding(result)

    def reset(self):
        self._iv = _bytes_to_bit_array(self.iv)

class tDES:
    def __init__(self, key, mode="ECB", iv=b'\x00\x00\x00\x00\x00\x00\x00\x00'):
        self.key = key
        self.mode = mode.upper()

        self.iv = iv
        self._iv = _bytes_to_bit_array(iv)

    def encrypt(self, pt):
        
        self.reset()
        keys = self.keys3()

        subkeys1 = _generate_subkeys(keys[0])
        subkeys2 = _generate_subkeys(keys[1])
        subkeys2.reverse()
        subkeys3 = _generate_subkeys(keys[2])

        if self.pad == True:
            if self.mode == "CBC" or self.mode=="ECB":
                pt = _add_padding(pt)
        pt = _bytes_to_bit_array(pt)

        result = []

        if self.mode == "CBC":
            for block in _nsplit(pt, 64):
                cblock = _xor(block, self._iv)
                cblock = _crypt_block(cblock, subkeys1)
                cblock = _crypt_block(cblock, subkeys2)
                cblock = _crypt_block(cblock, subkeys3)
                self._iv = cblock
                result += cblock
            return _bit_array_to_bytes(result)

        elif self.mode == "OFB":
            for block in _nsplit(ct, 64):
                self._iv = _crypt_block(self._iv, subkeys1)
                self._iv = _crypt_block(self._iv, subkeys2)
                self._iv = _crypt_block(self._iv, subkeys3)
                cblock = _xor(block, self._iv)
                result += cblock
            result = _bit_array_to_bytes(result)
            return result

        else:
            for block in _nsplit(pt, 64):
                ct = _crypt_block(block, subkeys1)
                ct = _crypt_block(ct, subkeys2)
                ct = _crypt_block(ct, subkeys3)
            return _bit_array_to_bytes(result)

    def decrypt(self, ct):
        self.reset()

        keys = self.keys3()
        if self.mode == "CBC" or self.mode == "ECB":
            subkeys1 = _generate_subkeys(keys[0])
            subkeys1.reverse()
            subkeys2 = _generate_subkeys(keys[1])
            subkeys3 = _generate_subkeys(keys[2])
            subkeys3.reverse()
        else:
            subkeys1 = _generate_subkeys(keys[0])
            subkeys2 = _generate_subkeys(keys[1])
            subkeys2.reverse()
            subkeys3 = _generate_subkeys(keys[2])
            
        ct = _bytes_to_bit_array(ct)
        result = []

        if self.mode == "CBC":
            for block in _nsplit(ct, 64):
                cblock = _crypt_block(block, subkeys3)
                cblock = _crypt_block(cblock, subkeys2)
                cblock = _crypt_block(cblock, subkeys1)
                cblock = _xor(cblock, self._iv)
                result += cblock
                self._iv = block
            result = _bit_array_to_bytes(result)
            return _rem_padding(result)

        elif self.mode == "OFB":
            for block in _nsplit(ct, 64):
                self._iv = _crypt_block(self._iv, subkeys1)
                self._iv = _crypt_block(self._iv, subkeys2)
                self._iv = _crypt_block(self._iv, subkeys3)
                cblock = _xor(block, self._iv)
                result += cblock
            result = _bit_array_to_bytes(result)
            return result

        else:
            for block in _nsplit(ct, 64):
                pblock = _crypt_block(block, subkeys3)
                pblock = _crypt_block(pblock, subkeys2)
                pblock = _crypt_block(pblock, subkeys1)
                result += pblock
            result = _bit_array_to_bytes(result)
            return _rem_padding(result)

    def reset(self):
        self._iv = _bytes_to_bit_array(self.iv)

    def keys3(self):

        chunk = len(self.key) // 3

        key1 = self.key[:chunk]
        key2 = self.key[chunk:chunk*2]
        key3 = self.key[chunk*2:]

        return [key1, key2, key3]

PC1 = [57, 49, 41, 33, 25, 17, 9, 
       1, 59, 51, 43, 35, 27, 19, 
       11, 3, 61, 53, 45, 37, 29, 
       21, 13, 5, 63, 55, 47, 39, 
       31, 23, 15, 7, 56, 48, 40, 
       32, 24, 16, 8, 0, 58, 50, 
       42, 34, 26, 18, 10, 2, 60, 
       52, 44, 36, 28, 20, 12, 4, 
       62, 54, 46, 38, 30, 22, 14, 
       6]
    
PC2 = [39, 7, 47, 15, 55, 23, 63, 31,
       38, 6, 46, 14, 54, 22, 62, 30,
       37, 5, 45, 13, 53, 21, 61, 29,
       36, 4, 44, 12, 52, 20, 60, 28,
       35, 3, 43, 11, 51, 19, 59, 27,
       34, 2, 42, 10, 50, 18, 58, 26,
       33, 1, 41, 9, 49, 17, 57, 25,
       32, 0, 40, 8, 48, 16, 56, 24]

# 64-bit to 56-bit permutation on the key
_KEY_PERMUTATION1 = [56, 48, 40, 32, 24, 16,  8,  0, 
                     57, 49, 41, 33, 25, 17,  9,  1,
                     58, 50, 42, 34, 26, 18, 10,  2, 
                     59, 51, 43, 35, 62, 54, 46, 38, 
                     30, 22, 14,  6, 61, 53, 45, 37,
                     29, 21, 13,  5, 60, 52, 44, 36,
                     28, 20, 12,  4, 27, 19, 11,  3]

# 56-bit to 48-bit permutation on the key
_KEY_PERMUTATION2 = [13, 16, 10, 23,  0,  4,  2, 27,
                     14,  5, 20,  9, 22, 18, 11,  3, 
                     25,  7, 15,  6, 26, 19, 12,  1,
                     40, 51, 30, 36, 46, 54, 29, 39, 
                     50, 44, 32, 47, 43, 48, 38, 55, 
                     33, 52, 45, 41, 49, 35, 28, 31]

# Matrix that determines the shift for each round of keys
_KEY_SHIFT = [ 1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2, 
                  1, 2, 2, 2, 2, 2, 2, 1]

_EXPAND = [31,  0,  1,  2,  3,  4,  3,  4,
            5,  6,  7,  8,  7,  8,  9, 10,
           11, 12, 11, 12, 13, 14, 15, 16,
           15, 16, 17, 18, 19, 20, 19, 20,
           21, 22, 23, 24, 23, 24, 25, 26,
           27, 28, 27, 28, 29, 30, 31,  0]

_SBOX_PERM = [15,  6, 19, 20, 28, 11, 27, 16,
               0, 14, 22, 25,  4, 17, 30,  9,
               1,  7, 23, 13, 31, 26,  2,  8,
              18, 12, 29,  5, 21, 10,  3, 24]

# S-boxes (Substitution Boxes)
SBOXES = [
    [[14,  4, 13,  1,  2, 15, 11,  8,  3, 10,  6, 12,  5,  9,  0,  7],
     [ 0, 15,  7,  4, 14,  2, 13,  1, 10,  6, 12, 11,  9,  5,  3,  8],
     [ 4,  1, 14,  8, 13,  6,  2, 11, 15, 12,  9,  7,  3, 10,  5,  0],
     [15, 12,  8,  2,  4,  9,  1,  7,  5, 11,  3, 14, 10,  0,  6, 13],
    ],
    [[15,  1,  8, 14,  6, 11,  3,  4,  9,  7,  2, 13, 12,  0,  5, 10],
     [ 3, 13,  4,  7, 15,  2,  8, 14, 12,  0,  1, 10,  6,  9, 11,  5],
     [ 0, 14,  7, 11, 10,  4, 13,  1,  5,  8, 12,  6,  9,  3,  2, 15],
     [13,  8, 10,  1,  3, 15,  4,  2, 11,  6,  7, 12,  0,  5, 14,  9],
    ],
    [[10,  0,  9, 14,  6,  3, 15,  5,  1, 13, 12,  7, 11,  4,  2,  8],
     [13,  7,  0,  9,  3,  4,  6, 10,  2,  8,  5, 14, 12, 11, 15,  1],
     [13,  6,  4,  9,  8, 15,  3,  0, 11,  1,  2, 12,  5, 10, 14,  7],
     [ 1, 10, 13,  0,  6,  9,  8,  7,  4, 15, 14,  3, 11,  5,  2, 12],
    ],
    [[ 7, 13, 14,  3,  0,  6,  9, 10,  1,  2,  8,  5, 11, 12,  4, 15],
     [13,  8, 11,  5,  6, 15,  0,  3,  4,  7,  2, 12,  1, 10, 14,  9],
     [10,  6,  9,  0, 12, 11,  7, 13, 15,  1,  3, 14,  5,  2,  8,  4],
     [ 3, 15,  0,  6, 10,  1, 13,  8,  9,  4,  5, 11, 12,  7,  2, 14],
    ],
    [[ 2, 12,  4,  1,  7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
     [14, 11,  2, 12,  4,  7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
     [ 4,  2,  1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
     [11,  8, 12,  7,  1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
    ],
    [[12,  1, 10, 15,  9,  2,  6,  8,  0, 13,  3,  4, 14,  7,  5, 11],
     [10, 15,  4,  2,  7, 12,  9,  5,  6,  1, 13, 14,  0, 11,  3,  8],
     [ 9, 14, 15,  5,  2,  8, 12,  3,  7,  0,  4, 10,  1, 13, 11,  6],
     [ 4,  3,  2, 12,  9,  5, 15, 10, 11, 14,  1,  7,  6,  0,  8, 13],
    ],
    [[ 4, 11,  2, 14, 15,  0,  8, 13,  3, 12,  9,  7,  5, 10,  6,  1],
     [13,  0, 11,  7,  4,  9,  1, 10, 14,  3,  5, 12,  2, 15,  8,  6],
     [ 1,  4, 11, 13, 12,  3,  7, 14, 10, 15,  6,  8,  0,  5,  9,  2],
     [ 6, 11, 13,  8,  1,  4, 10,  7,  9,  5,  0, 15, 14,  2,  3, 12],
    ],
    [[13,  2,  8,  4,  6, 15, 11,  1, 10,  9,  3, 14,  5,  0, 12,  7],
     [ 1, 15, 13,  8, 10,  3,  7,  4, 12,  5,  6, 11,  0, 14,  9,  2],
     [ 7, 11,  4,  1,  9, 12, 14,  2,  0,  6, 10, 13, 15,  3,  5,  8],
     [ 2,  1, 14,  7,  4, 10,  8, 13, 15, 12,  9,  0,  3,  5,  6, 11],
    ]
]

def run_unit_tests():
    
    # Test add padding
    test1_result = _add_padding(b"CSC428")
    assert test1_result == b"CSC428\x02\x02", "Unit test #1 failed: _add_padding(b'CSC428')"
    
    # Test add padding
    test2_result = _add_padding(b"1234567")
    assert test2_result == b"1234567\x01", "Unit test #2 failed: _add_padding(b'1234567')"
    
    # Test _rem_padding
    test3_result = _rem_padding(b"CSC428\x02\x02")
    assert test3_result == b"CSC428", "Unit test #3 failed: _rem_padding(b'CSC428\x02\x02')"
    
    test4_result = _rem_padding(b"1234567\x01")
    assert test4_result == b"1234567", "Unit test #4 failed: _rem_padding(b'1234567\x01')"
    
    # Test _bytes_to_bit_array
    test5_result = _bytes_to_bit_array(b"\x01")
    assert test5_result == [0, 0, 0, 0, 0, 0, 0, 1], "Unit test #5 failed: _bytes_to_bit_array(b'\\x01')"
    
    # Test bytes to bits
    test6_result = _bytes_to_bit_array(b"\xFF")
    assert test6_result == [1, 1, 1, 1, 1, 1, 1, 1], "Unit test #6 failed: _bytes_to_bit_array(b'\\xFF')"
    
    # Test _bit_array_to_bytes
    test7_result = _bit_array_to_bytes([0, 0, 0, 0, 0, 0, 0, 1])
    assert test7_result == b"\x01", "Unit test #7 failed: _bit_array_to_bytes([0, 0, 0, 0, 0, 0, 0, 1])"
    
    test8_result = _bit_array_to_bytes([1, 1, 1, 1, 1, 1, 1, 1])
    assert test8_result == b"\xFF", "Unit test #8 failed: _bit_array_to_bytes([1, 1, 1, 1, 1, 1, 1, 1])"
    
    # Test _nsplit
    test10_result = _nsplit(b'ABCDEFGHIJKLMN', 3)

    # Test permute
    # test11_block = [0, 1, 0, 1, 1, 0, 1, 0]
    # test11_table = [3, 1, 2, 7, 5, 4, 6, 8]
    # assert _permute(test11_block, test11_table) == [0, 0, 1, 1, 1, 1, 0, 0], "Test #1 for _permute failed"
    
    # Test lshift
    test12_sequence = [1, 0, 1, 1, 0, 1, 0, 0]
    assert _lshift(test12_sequence, 2) == [1, 1, 0, 1, 0, 0, 1, 0], "Test #1 for _lshift failed"
    assert _lshift(test12_sequence, 4) == [0, 1, 0, 0, 1, 0, 1, 1], "Test #2 for _lshift failed"

    # Test xor
    test13_x = [1, 0, 1, 0, 1, 0, 1, 0]
    test13_y = [0, 1, 0, 1, 0, 1, 0, 1]
    assert _xor(test13_x, test13_y) == [1, 1, 1, 1, 1, 1, 1, 1], "Test #1 for _xor failed"
    assert _xor(test13_x, test13_x) == [0, 0, 0, 0, 0, 0, 0, 0], "Test #2 for _xor failed"

    print("ALL UNIT TESTS PASSED")

def run_integration_tests():

    # Test subkey generation
    test14_encryption_key = b"\xEF\x00\xEF\x00\xFF\x80\xFF\x80"
    test14_expected_subkeys = [ [0,1,1,0,1,1,1,1,1,0,1,0,1,1,0,0,0,0,0,1,1,0,1,1,
                   1,0,1,1,1,0,0,0,1,1,1,0,0,1,1,0,0,0,0,0,0,0,1,0],
                  [1,0,0,1,1,0,0,1,0,1,0,1,0,0,1,1,1,1,1,0,1,1,0,1,
                   0,0,0,0,0,0,1,1,0,0,0,1,1,0,0,1,1,0,1,1,1,1,0,1],
                  [1,0,0,1,0,0,0,1,0,1,0,1,0,0,1,1,1,1,1,0,1,1,0,1,
                   0,0,0,0,0,0,1,1,0,0,0,1,1,0,0,1,1,0,1,1,0,1,0,1],
                  [1,0,0,1,0,0,0,1,0,1,0,1,1,0,1,1,1,1,1,0,0,1,0,1,
                   0,1,0,0,0,0,1,1,0,0,0,0,1,0,0,1,1,0,1,1,0,1,0,1],
                  [1,0,0,1,0,0,0,1,0,1,1,1,1,0,1,1,1,1,1,0,0,1,0,1,
                   0,1,0,0,0,0,1,1,0,0,0,0,1,0,0,1,1,0,0,1,1,1,0,1],
                  [1,0,0,1,0,0,0,1,0,1,1,1,0,1,1,1,1,1,1,0,0,1,0,1,
                   0,1,0,0,0,0,1,1,0,0,0,1,0,0,0,1,1,0,0,1,1,1,0,1],
                  [1,1,0,1,0,0,0,1,0,1,0,1,0,1,1,1,1,1,1,0,0,1,0,1,
                   0,1,0,0,0,0,1,1,0,0,0,1,0,0,0,1,1,0,1,0,1,1,0,1],
                  [1,1,0,1,0,0,0,1,1,1,0,1,0,0,1,1,1,1,1,0,0,1,0,1,
                   0,1,0,0,0,0,1,0,0,0,0,1,1,0,0,1,1,0,1,0,1,1,0,1],
                  [1,1,1,0,1,1,1,0,1,0,1,0,1,1,0,0,0,0,1,1,1,0,1,0,
                   0,0,1,1,1,1,0,0,1,1,1,0,0,1,0,0,0,1,0,0,0,0,1,0],
                  [1,1,1,0,1,1,1,0,1,0,1,0,1,1,1,0,0,0,0,1,1,0,1,0,
                   1,0,1,0,1,1,0,0,1,1,1,0,0,1,0,0,0,1,0,0,0,0,1,0],
                  [0,1,1,0,1,1,1,0,1,0,1,1,1,1,1,0,0,0,0,1,1,0,1,0,
                   1,0,1,0,1,1,0,0,1,1,1,0,0,1,1,0,0,1,0,0,0,0,1,0],
                  [0,1,1,0,1,1,1,0,1,0,1,1,1,1,0,0,0,1,0,1,1,0,1,0,
                   1,0,1,1,1,1,0,0,1,1,0,0,0,1,1,0,0,1,0,0,0,0,1,0],
                  [0,1,1,0,1,1,1,0,1,1,1,0,1,1,0,0,0,1,0,1,1,0,1,0,
                   1,0,0,1,1,1,0,0,1,1,0,0,0,1,1,0,0,1,0,0,0,0,1,0],
                  [0,1,1,0,1,1,1,0,1,1,1,0,1,1,0,1,0,0,0,1,1,0,1,0,
                   1,0,0,1,1,1,0,0,1,1,1,0,0,1,1,0,0,1,0,0,0,0,0,0],
                  [0,1,1,0,1,1,1,0,1,0,1,0,1,1,0,1,0,0,0,1,1,0,1,1,
                   1,0,1,1,1,0,0,0,1,1,1,0,0,1,1,0,0,1,0,0,0,0,0,0],
                  [1,0,0,1,1,0,1,1,0,1,0,1,0,0,1,1,1,1,1,0,0,1,0,1,
                   0,1,0,0,0,0,1,1,0,0,0,1,1,0,0,0,1,0,1,1,1,1,0,1] ]

    test14_subkeys = _generate_subkeys(test14_encryption_key)
    assert len(test14_subkeys) == len(test14_expected_subkeys), "The number of generated subkeys is incorrect."
    for i in range(len(test14_expected_subkeys)):
        assert test14_subkeys[i] == test14_expected_subkeys[i], f"Subkey {i+1} does not match the expected value."

    print("ALL INTEGRATION TESTS PASSED")

def run_system_tests():
    osecret_key1 = b"\x88\x99\xaa\xbb\xcc\xdd\xee\xff"
    ociphertext1 = b"<o\xb9\xe9_\xca\x94vK\x94\xb4\xabL\x1d\x1e\xf6\t%\xba\x977\x8a\x01]\xc6c\xffu\xc6\x11\x1b\x1c\xa0\xfcZL\xaa\xea\x9c\x8e]\xb0e\xe0%\x85\xb2\x8a\xabp\xba\xf1\xed\xde&\xa9\xb4\x00tg\x89K\xea\xd6\x08\xd0\xc5|\x95q\x8f\xddc\xe1\x1bi\xf6\x94\xd5\xaef1\x00\xafw\x96\xe3\x0e\t'\x17\xb2\xf7\x80GKM\xf9\x80\xc1\x08\x9e\x93J}\x1d\xaa\xe8 \xca\x9fC\xd3\x059G\xf6\x9b\x1eU\n\x07E\xd3\xcahi!\x94E\x90\xd8\xd9\tZ\x81(`,3<VR\t\x18Z\x93r\x12\x8d\xf3\xc5m\x16\xb6\xf6\xb9h*\x95\x97\x17\xaf$]!\xc4r/\x96.O\xd3_\xa2+\xd1\x82e\x10\x03\xad\xd7("

    # CBC - Cipher Block Chaining
    osecret_key2 = b'\x11\x22\x33\x44\x55\x66\x77\x88'
    oinitvector2 = b'\x01\x02\x03\x04\x05\x06\x07\x08'
    ociphertext2 = b'++\xf4\x1e\x88\xb8\xa8\xdc6\xebW|\xaa\xa2\x93\x11LK\xe6:\xcd\xae\x07Z\x80}vY\xfb\xc4<\xd9>\xc3]uf9s0\xc2\x96{\x9c\x86cR\xc3\x98L:\xbf\x82\x1d[\xd3J\x86H\x08\xa1C:}\xa1\xed1sa\xe06H#\xc1\xe35.\x81\x95\x93\xc6K\xe8\xa9\xb43\x8f\xa6\x02\xf8Ij\xcdHY\xc9\x83~%|\xed\xc4S\xa1\xe2\xcf\x91\'g\xd6}{\xedfe\xe6?\xcc =\x0c\xd4F\xf6~\x19\xa1\x9eY\x90z\xa4cH\x00k\xae\x9d5#Hme\xe8\xdf\x1f\x8a\xf9<\x94%\xd6\xfc\x9e\xa7\xb4\x1c \x7f\xb6-\x15c&\xa3\xcb\xfc\xaf\x00\xb1zS\x8e\x98\xe9\xc49Q\xcc\xe6\xbe.\x0c \xf7\xa8\xd3\x046\xfcYZ\xc6%#\xfe\x8f\x17\xc4F\x8e5\xd4\xfe\x0b\xd0\x89\xe2\xde\xf9\tJI\xec\x954|Xb\xd0\x90\x0f\x93\x16M\x0b\xcc\xa7\x1f\x91\xb8\x14J\x08\x07q\xac\\\xb2\xc7\xcdSw3=\xfe\x82\x97\'Q\x92q\\\xd4\xbe\x9b\xea\x1d\x7f\xc0w\xb42\xadX\x7f\xab\xb7e\x07}B\x84X\xfd\x9d\x90\xc3Q]\xf6\x98c8f&\x86\xdf\xd1\x8d\x153 \x9d\x00\xc6a\xfc\xde\t\x18\xd1)\x80\x8cb\x0e6<F\x10\xcc\xe1\rU2A\xedl\x7f\x88\xda\xe9[C\x89J\xbb\x99\xbd\xcb\xd2\xb6L\xcc\xb6&\xb5-\xd6\x03\xf2lJ\xf0^h1\x15\xc9\xf9;\xaa\x88;\xb9f\xbf\xb8v\x9cGLu\xcc\x82738\x86\x94\xdf[p\xed\x0e\xa7>?H\xb2\xac\xda\x86\xc9FDK;\xfc\x9a\x9f\x80\xf7\xd3c\xf8.9p\xc3\xaf\xecD\x8ek\xf7`\xf9~"OZ\x91\x135\xcf\xb9\xe5\xd4\xd3SD\xa5\xff\x8d\x9f\x1d\x1d\xee\x08\xcf\xd1?**\xf2\n4\x08\xd4,\x83\x95X|\xb2\xc5h^\xb9z\xefZ\xd4\xbbGW\x1a\xa3\x91\xd7\x89\x00AQ\xcc&\x84\x0eA\xe2\x03\x9a[Rz\x00\x95\x0e7Hm\x012\x87\xdfsWo\xd6Ka\x10\x80c\xd2\xd0\x94^F\xe1,yZ3z5S$yVE\x06\xbe\xad\xa0={\x15G30.\xba0\xf12b\\E\x0e\xa3\n\xd1\xe9\xa1HF\xf5\x0b\xab\xec\xd8\xdfzn\xc18-9\x83]2\xe2"\xd0n8\xb3\xf9\x8e\xd2fPm\x01\xaci\xce\xe0=zS\xc0nr\xc6\x88\xe19(\x0e\xc2\xe3\xb1s\xe5-\xffr5h\xedB\xc2\xdd\x9b\x04\xc99\xec\xef\x11kU>\x98v4\\\xf2\xef`7!\xdb[\xcf\xfcD\xf8\x0f!\x85\xc0\x8bn\xc9\xcf\x99\xdc\xde:\xaav\x88\xcc`r\x8c\x8c\xe0\xf4+\xf1\xdf\x8d/\x82OC\xba\xd4\n\x83\xe2\xd8\xff\xd7\xcb2\xea\xeb"\xde3\x08R\xea"\xb6\xb2\xfe\xc2\x15\xdai\x81\x95\r\xe3r<Y\xad\x95(\x1cT\xd0Q(\xea6\x1f(W|\xef[af\'\xaa_\x9b\x1c\xd1]\xac\x14\xe3>\xfd\xf5S\x1ax\xf9\xe5\x8f ~\xe6\n\r\x7f\x1f#\x1fq\xd8\x97\x00\x8c'

    # OFB - Output Feedback
    osecret_key3 = b'\x01\x23\x45\x67\x89\xab\xcd\xef'
    oinitvector3 = b'\xff\xee\xdd\xcc\x11\x22\x33\x44'
    ociphertext3 = b'\x94\x80\xf7\xbd@`\x05\xdb\xcc\n$ \x92|\xcb.\xaa\xd8y=\x9ex>\xfe2&^]^qqv0 \xd2t|\xf9T\xf6\xc8[6\x1f\xfe72\xa0c\xe2\x1b\xa0\x9d\x07`>D2\xd9X\xb8"\x81\x04\x81 \x00\xa5^|\xe2\x96X\xf8\xa4\xfbl4\xba\x94\xd5\x040r\xabf\x07\xed\xaah\xf8|6\xcc%b\xe95\xf3NY=E<\xd8B\x1er\x14\xa46\x03N\xdddw\xae\xb0a\xb2\xb5\xb8a9=\xc0S\xe8"\xb8\xc0\x1cH\xb1\xaao?`-R|\x9a\x03\x87)\x00\xfbq\x99\xcd\xd2\x156\x0c\x94\xac=Q7$S\x06\x88I\xbblG\xfaAdCS\x1c0\x8e\xe6\xcbs\xaa\x98\xd5\xbdgR)o%br\xdb\xd4\x99i\xa5\xf4eU\x9e\x1f\xcf\xd6\x0c\x84 \xd9s\xc7`\xa2sm.\xce\xc4\x8c\xae\xc6+\xbe\xbc5\x8c\x1f\x19\xa0\xc0}\xb3X\xd3\xaa\xd8\xe8\xbcT!\x06\x1b\xe6.\xca\xac\x15\xbc\xe9\xb5%\xcb\xe2K\xdbW\x1f\x85\x92\xbcuz\x8d\xf5\xc8\x1b\xe9\xfcXq\x1e\x97h\x1a\x8e\x99Q%\x7f&\x11\xd7\xe32\xb8\x86\xce\xd4"Cpp\xa7\x99J\xd3\xa2\x04!\x07|\x13]R\xda\xb6\x90@\xfa\xd6T\x81\x01Z\xbaQi\xbf\xdb\x19\xc0\xf0\x19\xa4y*\xfd\xed\xe0\xc7\xa0F)\x08\xa0w\x93.\x8dr\x115\x18\xd9/\x19\x16]\x9d\xfa\x86\x0f\'2\xdb\xbd\x9f=\x99\xa1\x95\xce\xdc\x85\x99\xaa\xab\xb2\xbc\xf9\xbe$\xdf&y\xc4\xf0B\xe9\xd0\xf0\xe93\xa5EX\xf8\x8ca\x1b\xc4\xafz\x14\x8dq\xc0U\xb8[\xca)\xeb:\xc6\xfb\x02Y\xfb\x7fj\x14\xbe\xf92\x8f\x9a\xa3-\xc8\x1e\xd3\xc7\x16\xe2i\x1c\'\x19y\x81\xac6Z\x86e"k?\x97n\xca?r\x06\x7fv\xf0\xa9X\xde\xaa\xdb\x1dK\x86\xd2\x19\xafY\xcb\xf0\x18\x9c\xbf\xea,]\xe5Pz\x02p\x19I/\xdd\xa5S\xf0Ke\xed\xfe'

    des1 = DES(osecret_key1, "ECB")
    print("\nDES ECB")
    print(des1.decrypt(ociphertext1))
    
    des2 = DES(osecret_key2, "CBC", oinitvector2)
    print("\nDES CBC")
    print(des2.decrypt(ociphertext2))

    des3 = DES(osecret_key3, "OFB", oinitvector3)
    print("\nDES OFB")
    print(des3.decrypt(ociphertext3))

    # ECB - Electronic Code Book
    tsecret_key1 = b'\xde\xad\xbe\xef\x7a\xc0\xba\xbe\xca\xfe\xf0\x0d\xca\x7d\x00\xd1\x23\x45\x67\x89\x0a\xbc\xde\xf9'
    tciphertext1 = b'.<\xef\xec\x03\x9d\xc6>\x03U\xde\xdc\xfe,f\xbe\xef\xe3\x15\x13\x8e+m\xb1D,\x10\x89\xf5g\xcaCh\x88.\xd3\xe3\xcf\xfb\xd1\x87\xc22U\xe4\x07\x02\x17\xe6)!\x06\x8c\xeeu\xc1\xc7\xa5!Yb\xe3!\xe7\x02\xeb\xd2h\x97/\x8aUf7\x12i\x1ez\x07\x82\xf2M\xcf\xf0&\xc9O\xf49:0\xfdv\x0cT.D\xddc\xfe\xd8t\x8b\xf4\xa1oq0G}\r\xb4b\x1c\x9a\xad\x98\xfe\xad\x8a\x1f)\x88g\x9d\xb4\xed\x01H\x05\x9c^\xd5\x84G\xb6\xa6N\xbeo\xdd\xa9:\xf3\x9e\x16\x9b\xd5S\xdc6\xed"\x08\x8eK3\x82\xe2\x04\xd8*\x96X$\xaf\xdc\xa7>\x9f\'\xef\x88\xba\xca\x9b\x9cMn+\x91~W\xde\xcfx\x811^<\x8aS,\x01f\t\x87j4\xb1?\xef\x99\xa0\x98\x0cS\xe5\xb7\xcb\x1e\xb3\x0b\x10\x86L\xa2\x02\x83\x830\xb1\x17\xd6W\xbeB\x0f\x8e9 "Z\xad\xa3\xaa&\x98^\x1d\x01mn\xa1<\xb0\xab\xf8[\x06\xd6\x17\x94\xd7\xbdk\x98\xb8\xfc\xa56\t\x10\xb0\xba\x9f3\xe5\xe9\x8a\x98,-\x08`\xa8Q}\xcd\x99\x99\xea\xaa\xb8\xfa\x82\xda\xca\x9c_\x9ag\xee\xdf\x03\xcc\x19d$S\xc2\xbcsj\x99h\xcd2\xb4JpA\xa6\x1b\xce\xa1\xd2\xe6\xc1\x82\xd9ux{\xa5\xa8\xae\xdb\xc7\xf2\xa1\x027\xbbg\xf7\xfc\xd7\x08\x9c+Ks\xf9\x16\xf9/\xd2\x94"\x99\xee\xd52<\x9a\xec\x7f%\xef\xce\xbbu\x05\x88\x9f\x087\xe8\xd3(~6\na-\xa0\xa4{\x83\xaeza^3\xd8m`\x9bl\xc3\xc1\xbdZ\x9e\xf5\xab0\xef*\xdd:\xb2|u\n\xf1K\xac\xdc>c\x1c\x9e:\rfnP-\x08\xdd\x96\x9e\x7f^ \x90\xb7\x16+\x96\x1f\xca\xc4\x98\xa8h\xf0r\n\x0brn\xf5Qa\x06\xb23\xa0i]\xd8\xed\xbd\xe0\xda\xb3Zx\x97fh\x83\xd1\'d\xe4\x99\xa6\x94\xb6L*\x0c;\x8b\xadj]I\x81\x1e1\x99\x15\xff\xd0\xc4\xa9\xac\x08M\xe1)\x06\xebV\x89q\x84\xa5\x88F\x12\x95\xa0e7\xb3\xbc|L\xf7\x01\xf3\x9f\xa02z\xcf\xca\xa9\xbd\xccQ\xb6\xba\x95\xb3\xfb\x8dO!W'

    # CBC - Cipher Block Chaining
    tsecret_key2 = b'\xde\xad\xbe\xef\x7a\xc0\xba\xbe\xca\xfe\xf0\x0d\xca\x7d\x00\xd1\x23\x45\x67\x89\x0a\xbc\xde\xf9'
    tinitvector2 = b'\x88\x99\xaa\xbb\xcc\xdd\xee\xff'
    tciphertext2 = b'\x9e\x8f\xe5G~\xd3\xeb\x9c\xd5\xe8\xb8\x1a\x17\xe5\xa1H\xebVX\xbe\xcf}W\xc8\xb5\xa6\xfb\xbd\x1fG\x8b\x13.\x1c*\x1d\t\xab\x1c\x8d\xf3#\xf8\x86\xf4\xbad\x18\x9fR\xad\xc7\xdd\xe5\xde\xf7\xd9\xca_\x1eY\xe4\x06-s\x86\x01\x0e\xdad\x15Z\x08\x92=6\x9f\xbc\x85\x8b\xfe\xd1\x9a/W 0\x16\xa1\x07\x04\x9dY\x8c\x85Z\xeb\x11r\xa3\xff\xb1\xbbd\xd9\xb8\xa7\x1d\x88\xdc;\xfb\x8d\xde\x04\x17\xb8\xde\xd5\xce*a\x93bQ`~\x17R\xec\xb928\x9f\x9d\xe4\xaa\x08.\xe9\xfdV\xf0\xa0\xa7`\xa1\xff^\x7f\xed,/El\xab%\x85\x91\xc3\xe2s\\\x96H\xc3\xceh\x8c\x91\x87\n\xa2u\x1b.@B!\xfbg71~)P\xa5\x9f\xd3R\xdb\xa1\xb33\xe7\xbc\xbc\xf2\x9d\xbf\x08\x99\xa3\xaf\xba\x16\x0eEh\xeb(/\x8cF`K\xe7\xaav\xe1\x9d\xc1\x98\xff\xf5r)e\x06\xa1\xa1\xef\x83W\xf9\xf3\t\xc4\x14p_:\xcc]\xca,\x11y\xdbf\xae\x9f\x7f\xb1Z\x95\\\xe3\xd4\x83A\xce\xc9\xe5\x97\x82pHv\x8d\x81\xcc\x9el\xa9}\x85A\xf0\xaf\x01B2\xd7\xc9\xe7Eff\xb5GY\x85\xd0\x01\xd2\xc9\x88N\x93\x86\x9a\xab\\T\xc2\xb9\xf6\\\\H\xed\xb0\xb5\xf8\x1azW\xc2K\x12\xfe\xc1\xd4\x86\x8c\xc9\xa6IU\x0c\xc4\xfa:\xd9c\x0c\xf4\x06\xf2Kg\x82D\x15\xc1_bG\x97\xbe\x9ed\xe8\x88\x87IS\xc1\xa6\x12\xb5\xa5\xe1.\xc5T\x191\n\xca\xa5\xfb\xe0\x92L`MG\xbd\xfa9\r\x7f\xb7U$^<\x1fx\xd3\xf6\xaa\xfaK\xbe\x81\xa6\x0e\xe5\x15#L\xfa\x1c\xc0\xa3\x08r\xb0~\xf6Jh\xf5\xf8\xfdx 3\xd2\xed\x87\xc2\x1c\x01\xea\xe9v]Vcl`\x8a\xb5\xcf\x08\xd0z\x00\xa3/\xc6\xa0\xaei*\x8b\xae\xd3\xb7\x87\x98B\xf2\x15\x08/N$\x80\x80\x0f6\x1c\r\x05\x12#:E\xd8\xf0vG\rv\xf8X\'\xc3\xa3\xc4\xda\xab,\xac\xecT*\x83\xc9\xd2tz(t\xe0\xa3d\xeb*\xc0D\xea\xbe\xbc\x18\xa4\xc7\xa0%a\x01G\x13\xa4\xb3\x12\xff!\xc2#\xee\xb7\xd4M\xfa\x9fTG2v\x14T\xd7\r\x1fJ\x90&\x80\x0fblPtG3`\xfe|~Q\x07h\r[$\xcdT:/\x94\xca\xce\x84\xd5\xa5@\xa0\xa6\x83\xba\x1b\xdf\x13~:hr\xa5\xad\x8b\x14\xfe\x1ae\xf3\x91\xe3\xd1\xe3\x99\xc0\xe9\xb7\xab\xac\x7f3i\x18\x8a\x1a"\xee\xc0Y<G\xea\xbf6\xba}2\x9a\xca\xf2OTM\xdeUQ\x13\xf3+\xdc\xcdj8R\xbb\x8a\xad\x1a\x16F\xf4`!\xc2\xeb\x12o\xf2\xb5\xefU\xc9\x01\x85l\xfe>\x15uF\x84\x1f\r\xfc\x8a{u\tLZ\xcf\xbd\x17\xb3X\xca\xc0\xa2\xaf\xb1\xb0\xb0>\x04\xdaK\x14\xb3\x1f\xd1\xabU\xb5z\xe4Z=\xa8\xf4\xc7\x9f[\xaf\xa2w\x9e#}\x9cO\xfa\xa8\xdb%\x8am\xfb1\xc2x\xa2\x9f1G\x02b\xa4c\xc7r\xa7yr\xe1-\xbc\xdfq\xcc=\x028\xc4\r\xf1x\x8bzc\xff`h\xdf(\x8eRS\xde\x8e\xa5\xc2<n\xcf\xfe\xe0\x8e\xb1\xd8\xc3N\xe9]\x1a\xe6\xaf\xf3DB\xc2\xa4:\xad>\xbd\xc2\xb1\x89\xe5\x98\xdb]\x14\x91\xf9\xdf\xcf\x11\x1f\xc5p\rr\xe0\xf8\x19S\x9f\xee\x08\r\x02\xafF/\xc7\x9a5UPb\x1a\x9a\x13Yv\xe3\xf9\xb3\x1d\xb5\x93\xe5\\HH\xc7\xe2\xd6}\x87\xc57g\x17\xa7\xbe\x96\x80"9u\x9a\x9e\xdc\xd7\xb8\xff\x96\xab\xa9\xd0\xee\x11CzIc\x16\xd9\x98X\x14\xe7\xcb\x89k\r4\x05@\x87\xc9\xf78\xb8\x9c\xba\xad+v\xee.\xacON\x94\xc8\xf3\xb7)\xfe\xcb\x97p\r\x94\x95\xd7\n\xdf\x144\x1c>\x0f\xfd\x08]\xa2\xb4\x05\n\xb5\xea\x0b\xeb\x11\x9e\x04A\x1c;\xb6\x00\xc9\xf3\x8d9K\x12\x7fE\x98\xeb\x10MM \x95)5\x9b\x01r\x9a\x96\x17m\xb4\xf7\xadC\xa5f\xf8y\n\x0c.\xd3\xf2\x06\x14Q_\xdf\x11\x80y\x0c\n\xccuu\x87\xeb~\x9f\xc4\xde\x83\x96a\xdc\xbc\xf6N\r?,\xf7+k\xde\xc7\x04\x1fJ\xc9&\x91z\xc8\xd5M{\xa6\xad\xc9\x9d\xcfF\x89^\xe3\xb8S\xabQ\xd1\xf4\x17\xc6\xd3\x99\xf4\xe8\xab1s\xc2A\x96\xdd\xd8i\x9f\xf6>Hu\x8b\xf7 "\x8c\xdf\xc7$U;\t2\x1ce\x1c\xf9l\x1d+\xe5\x05\xd3d\x98?\xc4\x14=o\xbb \xd9\x01\xb3\xbb\xa2\xc7o\xc1<f|\x8e\xb1^\x95\xf6\x98\x03dy\x1da\x94uH\x94\xeb\x039d\xd9\x107\x13\x16\x80\x7f\xd3X\xd4\x95\x070ye\xc75\x8e*de\x06\x05U+\x1d\xdf\xf3\xf1\xb5\x06K\xf4\x7f"{ \xdd5|\xd2G*\xd2\x06\xc8\x10\xac\xed\xe2\x1f=\x06'

    # OFB - Output Feedback
    tsecret_key3 = b'\xde\xad\xbe\xef\x7a\xc0\xba\xbe\xca\xfe\xf0\x0d\xca\x7d\x00\xd1\x23\x45\x67\x89\x0a\xbc\xde\xf9'
    tinitvector3 = b'\x88\x99\xaa\xbb\xcc\xdd\xee\xff'
    tciphertext3 = b'\xaa\xa6\\6\x9f\xbb)\x1b\xb2\x14\xfb\xf2\x88\xebQ?\xa3\xaf\x8b|l\xdaG>\xd1\x84\x83l(\x18\x9a\x1cG\x11t\x9b\xf1\x9b<\r)SD \xd0\x01\x05\xc5\xdb\xed\x8e\x1a)\xbd\x8c\xfcG\xbfB\xf2\xc8%R\x04\x8a\x92{\xc1VPV\xea\x98\x1e\x0e\xfaA\xcb\xb6!\x96]wA\x98\xbe*\x86\xb3\x1a\xdc$\x85x\xe1HM\xf5Z\xcd\x10\xfc\xa6d\x17\x0f#\xb7\xdcu\xbe\x04B46\x1a69c\x10&\x0f\xb0,\x85\xb8\x04\xa7\x9f\x95\xe3\x06\xf3\x17L\xd7\xff\x8c\xee\xf42\xb7\xa9\xfcJuB7\x83\x83\x8b\x89Eq8\x80\xb4\x7fQ\xa8\xd089O\xf6\xc81j\xc3u\xb3[\xcb\xe5,P\xebqT\xe5\xf9\xc1\x98\xd3\x1b\x9c\xb6\'v&\x14\x86-\x1c^\xad\x7f\xd2\xcb\xb9t(gh\xb9\xc5\x9c$\xdc@\x86\xa1\xc2\x98v\x9a\r\x05\xef\x99\x89\xe3\xcb\xe6\x1a\x89t\x04;\xb5@@E\xc2\x15\x9a\x9f6\xaf8\x9c\x04E\x08Qf\xb7\xbeD\xdc\xf8\xbag*?\xd5Zl\xa4\xabW\xcc[S\xe9"\x03c\xc7\xb0\r\xe0\x17+(.\x85?\x06\xbak\xdc\x8b\xba6A-\xf7c&\xc2\xbets\xb0\x0e\xe7h\xe8\xd6\r\x1a\x8d\xd7\xad8\x8b\xf4h\xdc\x15\xe3\x04\xf6\xbc\xe2\xae\x04\n\t\r\x83(k4\x0e\x15\x90\xeb\xc9z\xfc>\x14H\xf0S5P\xd3\x86\xacpn\x1f\xcc\xeej\x1b_\xeb\x1f\xcc\xeb\x01\xad\x16G\xab2w\xc0\xa7\xcb\xd6\xbd\xad9\xd5\x1f\x1cu\x9c6l\x9aQ\x8f\x8cu#\xb829s_\x05h\x90\x847J\xa4\x87`\xc9\xb0\x8d\xf8HGRw\xe6e\xbe\xb5\xfc\xa2\xfc\x1c\xc6"\xb7\x11%\x8c#\xe3\xeat\xf9\xf0\x1f\x08>o\x11\xe4X)\x8e\x08\x1e:\xc9qP\xc0p\xe5t\x98\xa7l\x91\x0c\x94\xe6c\x98E\xac\xfb\x13p\xd5\xc3/et- \xa6\xa2\x9d\x04\x18\xe0\x0b\xea\xe1\x96\xec\xb6^\x8d\x99\x80\xc2\x93\x8c\t\x8d\xf8\x10\xad\x8aD\xcc\x9cc\xb5ZR\xbc>6\x169\xect\x99\xa8Dn\x82\xff\x99\x1f\x07\xccX\xdf\xc0\xe5\x9e\x8dR\xc7\x89\xa98\xf2S\x86\xddI\xa6\x89\xd3rO\xf1\xeb\xf7&\xe8*\x93L^#\xa5\x95p\x99\xcb\xb0\xb2\xad\xf0\xfc\x80\xd2\xe2\xcd\x01\xb7\xccF\xda\x04\x8ed\x19K\xb4\x17\x81\x1aZ*/k\x0c\xdb\xb2\x03[\x14\x03-j\x0c%\xe3\xe6\xa3\x0e\xb61\xcf\xbe\x8f\x18\x06\x85\xf8\xf4r\xc0r \x03j\x02\xe9\x0f\xc4r\xe1\x01xw\xbe>6~\x84\xe9\x8d~N\xdc/\xfb\xb2\x18C\xfd\x9b\xfe\x81~\xa2\xfe\xef\xcew \xb8\x02\xe4\xb9KV]\xb7\xbb\xe0\r\xe1\x8f|\x84\xc0a\x1bZ8\xb3E\xc4\xd0M\xed\xa4\xd7\x92gR.f\xae\xb6\xc1`rT\xd6\xd4\x96-\x05\x0e3JL\xcf\xfe*\xf7lAx\x85Fgnz\x8byc^]\x9a\r\xce\xab\xc1/\xab\x0cG\xd0\xa9\xec\x94\xb2\xe6\x16\xfa\xfc\xc1M\xd2Xk\x0c>\xc4\x0f\xcd+\x82\xb7\xdbs5\x03\xf8\xc8vF\xb9FI\xfe\xc7T|\xbb\xfe1@I\x12\\#h\x96\x04\xf2\xb0^\xd4\x8c\xdaL\x1b\x1a\x83\x0f\xf9i\xca\xc5\xea\x01\x1f<,\xbc;6`R\xebf`Y]\xff\xc5<?>\xc9\xed\xca\xaf\'\x9d"\x83\x03/G!|\x86\xd8\xb7\x15P\x80\x14\x0e(?\xfe\x1c\xf9\x92f5\x1f\xb9\xa4\x17\xad\xba\xa9Ev\x84pr\x85\x99\x18\x97\x14\xaa\x8dg\x05\xaa\x0cop3\xa7\xa53\xe7\x1f5\x8a\x86Y\xe5:&\xad\x05X\xee=ev\x93\xb3\x06\xb0RJA\x17Rz\x12\xd8u\x93n}\x15P\xca\xc9\x08\xdb/\xd4\xecz\xbc\xf5\xba\xf7a\x9b\x81H\xda\x1aV\x08\xa2\n\x18\xcf\xe1/\x87L\xf6_7\x8c\xed\xfc\xeez\x16\xb2y\xe1\xc9(D\x175E\x91\xb2\xfe\xbb\xb1l=\xa3\x0f5s`\x1d\x0f\x04\x96&\xe0\x91@7\x91\x94\xf8\x1d\xf4\xccX\xd3k\xf4f\xfb\x81\xfb\n\r\xc8\x02&#n\x82)\xa7\xc4x\x8c\x161|z3\x0f\xeb\xd3g<\x86!f \x13K\xab\xcb\x93zqM\x03]\xc9PDaWbe\x1c\x01\xa6\x97\n \xd4\x8eKD\xbf]S\x81\x8f\xd3y\xd2\x08Z\xd9\xd9wc\x93\xb2]\xa7\x1c\x94\xe1e\xf0\x92\x9e\xe1\xb3r\xfe\x80\xf3J\xad\x0beq\x94\xfe\xa3\x15\x85%Z\x00\xe1\xc227\x95/\xfe\x0b\xf2\xfe\x93xE\'"\x9f\xca\xe1\x17\x8ds\xfe\xdc\xc1z\xe7Q\xca\xee\xb3\xf0\x845\xde3\x87C1\xc9\x0e\xa6\xfc\xf7\xa4\xa1#\x9fg\x12\xf5\xe7\xffG\xd7\x8b\xc1n6\x9aQ\xbc\x9fhY\xe6C\xd2\x16\x8b\xa0\x84)\xb8Y\x1b\x1d\xf0x\xd9*\x1f\xe3\x16\x86)\xa4\x91\xbfS\xea\xecV\xef\xec\x04\xc8\xa7\xc6g\x9eq\xe9m\xc4\xc0\r\x81f\x86}GNwq_KzX\xab\x16\xf7\xf6\xfbS\xe0\x97\xc9\x95/1a\x12\x01k\x0f\xe7\xed\xe4\xe6\x15\xb8p\xd1\xbd\xe9\xc1Nn\x96\x84y[\xb54?\x00\x86N\x1e\xeb.\xea\xd0\xae\x068\xc2~\x1fj6\xe5i\xb3\x9a\xbc6\xb6\x95\xcc\xf7>GZ\xf9v\x8c\x9f\x17_@\x9e8\xcd\x19\xd9\xa0\xe0\xcc\xb1\xf3\x05\x90\xeaKu\x19>\x9cYN#)\x0b\xa7\x97\xae?\x13\x0f\xe7\xd3\x7f!\x1b\xecG\xa7\xf2\'\x90\r\x87\xee\xee[\xd3vF\x88\xca1\xb8\xc9\x1d\xd3p\xb1\xe7\xad\xd09\x06\x1f\x02\x00W\xd9\x9b\x99d"fnz\x90;\xe3\x03\x06\x9b\x92\xc3\x03xq\x97g\xe6\xadR\xce(\xf9\x8c\xa4N\x86\x1fB+Y\xcd\xc1\xba\xbc\xa2\x1c8\xd2\xb1\xccP\xe2\\\xfa\x9e@\xca\xfbS\x9fp\xba\xab\xa8\xee\xe0\x8e\xdf\xbc#\xacd\x1aP\x1c4\xady\x17N\xe3\xc9\xe9<\xf0\xcfR\xb6\xa6p\xcf\xc8\x16[v\x9d"\x1fS\xebhCZ\x1f3\x13_\xc8\xb5\xb0\xaf\xe7F\xd9\xb98\x1a\x0c:`P\x01\x8b ^\xca\x94w7\xd5\xb5\xd2\x88|K\r\xa7:\x00\xe0\t\xedy\xa1\xc80\xd0g{\xa5\x85\xed33%J9\xdf\x19\x11rk\x0b]3Q\xda\xd0\x14\xe9\x98\xaeD&\x1b\xb9\x00\xb8\x9b-gI=\x19\xbf4E,\xfb<\x10\xf5\xf66/\x08\xcdy~&9\xfe\x8cf\xfeg\x13\x1dM]\x94\xcc\x17\xadid\xd6\xcb\xfaU\xf0\x95\xa5\xa1\x19<j\xaf\xe1z\xdb\xfe\x94\x9a\x85y\xcc\x14^\x8d\x1b\xd5\x0c\x1a\xe2z/\xf9\xe1\t/\xa4I\x80w\x8c\xcd\xe0\x97\xddi\x90\xed\xe0\x04-\xa3\x06\xc2\xddv9\xff\xb2l\x1b\\G\xd7cL1\xcb\x07\xafm\xb7)\xf7\x08\xef\xe7\xac7\xcd\x04\x0cd\x0cP\xff\x06\x97WFv\x8c\x9e\x054\xe09\xbd\xe5Io%\xf54\x9d\xab5\xea\xd1\xcb\xfe\xbe\xe11<B\xb6\x03y5\xe6\x98\xda<\x17gR\x84\x94J\xd3*E)\xab\xffG\xd5\xf3\xab\xaf\x02\xf9hE+\xc8\xd5\x87\xad\x95.N\xf1~\xca\xda\xd8MJ\x94\x1a\x02i\xe3\x8c\x11\xb0oU\xa6\x04\xb0\xdb\xd0D\'\xe7\x83\xb6\xd8\xad\xdd\x8d\xe65 u\xd3\xb8\x0b\xcc\xe1\xf1\x8av\x1a\x05\xee\xf1\x02\xbfz\xed1\x8a\xbb\xa1)\xe2P<\x81z\x14\x92/\n\xc9\xc8\x82\x9c\x85\xc4tc\x82[\xa2Q\xbb\x99\xc0\x9aP\xddZ\x11\xde\x0c\xb4\xd0\xcbl\xf6\x1e\x9b\x90S&}%m(\xed@\xcff\xea1\'\x83H\x93\xcb|f\xad\x8bvt\x80\xe5\x84\xac\x92\xee\x8d$\xc3\x8b\xb8\xc5X\xf5\x96O\xe1\x83L\x8b\xf3\x00\xb3\xf2\x13\xa2*J\xeb\x15\x85\x19*\x7f\xd3\xf1w$\xee*\xaf=<\x0cb\xe4c\x16\xa96\xe691\x06\xcd\xcc4\x0e\x9f_\xc4\x18\xb9\x1aEm\xcc\x01\x98\xb4Ns2\xc7WAg\x04\x8eM*\xc5\xc9\x8d\xbb\xfd\x84q&\x94V\xa0\xb4\xd74\x8ea\x9dY\x8bo\x86\xf6\xdeH\xcd\xff\xf4\xe5\xd9\xe5H\xc8ML\xf8\x94\x80\xb8\x88\x00\x82\xee\xe7\x9eN\x1f\xaeA\x85\xd9\x8f\x8b\x87\x8d\x94Tu\n.\xc0\x9d^\xe4\x8e\nt\xbbP\x93\xea\x01\xd9C|L\xdc\xf4\xcd\xaf\xbet\x95\x90\xafy\xff\x9b6\x91\x87\x1d\xa9\x16l2\x8d\xf8\xf0\x07Z\xb5\x938]\x0b\x1e\r\x1d\xd9\xea\x06G\xae\x06\xa0'

    tdes1 = tDES(tsecret_key1, "ECB")
    print("\nTriple DES ECB")
    print(tdes1.decrypt(tciphertext1))

    tdes2 = tDES(tsecret_key2, "CBC", tinitvector2)
    print("\nTriple DES CBC")
    print(tdes2.decrypt(tciphertext2))

    tdes3 = tDES(tsecret_key3, "OFB", tinitvector3)
    print("\nTriple DES OFB")
    print(tdes3.decrypt(tciphertext3))

    print("ALL SYSTEM TESTS PASSED")

if __name__ == "__main__":
    run_unit_tests()
    run_integration_tests()
    run_system_tests()