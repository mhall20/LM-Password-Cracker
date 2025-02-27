import cui_des # Changed my des function to take an input to add padding or not
import json
from itertools import product # for combinations

# Had to do some research on common substitutions because
# the modual I wanted to use did not want to work with me
def _leet_combos(word):
    ''' Generates combinations of l33t for given word '''
    # Most common l33t substitutions
    leet_dict = {
        'a': ['a', '4'],
        'e': ['e', '3'],
        'i': ['i', '1'],
        'o': ['o', '0'],
        's': ['s', '5', '$'],
        'z': ['z', '2']
    }

    # Create list of lists for l33t
    # .lower for consistency - it's fine since we use .upper later
    substitutions = [leet_dict.get(char, [char]) for char in word.lower()]

    # Make all combinations by going through list of lists of substitutions
    combinations = [''.join(combo) for combo in product(*substitutions)]

    return combinations

def _lm_encode(word):
    """ Generates LM hash from input """
    # Turns word to upp and adds null bytes if it isnt 14
    word = word.upper().ljust(14, '\x00')

    # Get both halves
    first_half = word[:7]
    second_half = word[7:]

    # LM hash key
    constant = b'KGS!@#$%'

    # Create DES classes for each half - no padding
    fh = Matthew_Hall_cui_des.DES(_add_bit(first_half.encode('utf-8')), mode="ECB", pad=False)
    sh = Matthew_Hall_cui_des.DES(_add_bit(second_half.encode('utf-8')), mode="ECB", pad=False)

    # Encrypt both
    first = fh.encrypt(constant)
    second = sh.encrypt(constant)

    return (first + second).hex().upper()

def _add_bit(half):
    """ Adds 8th bit for the halves """
    key_bits = Matthew_Hall_cui_des._bytes_to_bit_array(half)

    bytes8 = []

    # Go through bits 7 at a time to add 0
    for i in range(0, len(key_bits), 7):
        chunk = key_bits[i:i+7]
        chunk.append(0)
        bytes8.extend(chunk) # Add new chunk

    return Matthew_Hall_cui_des._bit_array_to_bytes(bytes8)

def _number_combos(word, max_length=14):
    """ Check for combinations of words with numbers """

    # These are the most common 3 and 4 digit number combinations.
    # You said that tallman password has a few numbers after,
    # so I looked up the most common number combinations for 3 and 4.
    # I wanted to do ALL number combinations up to 4, but I don't have
    # time to let the code process for two full days
    specific_combinations = {
        '000', '123', '111', '222', '333',
        '555', '666', '777', '888', '999',
        '321', '654', '1234', '1111', '0000',
        '1212', '7777', '1004', '2000', '4444',
        '2222', '6969'
    }

    combinations = []

    # Run through and add the combinations
    for combo in specific_combinations:
        combined_word = f"{word}{combo}"

        # Double check to make sure its still the 14 character length
        if len(combined_word) <= max_length:
            combinations.append(combined_word)

    return combinations

# Each time a word is added, it prints to terminal so that you don't go crazy trying to figure out if it's working
def generate_table(dictionary_file, output_file):
    """ Create a rainbow table of LM hashes and jave to JSON """
    with open(dictionary_file, 'r') as f:
        words = json.load(f)

    rainbow_table = {}

    # Go through word by word and append it
    for word in words:
        if len(word) <= 14:
            word_hash = _lm_encode(word)
            rainbow_table[word_hash] = word
            print(word)

            # Append l33t substitutions word by word and every combinations
            leet_combos = _leet_combos(word)
            for leet_word in leet_combos:
                if len(leet_word) <= 14:
                    word_hash = _lm_encode(leet_word)
                    rainbow_table[word_hash] = leet_word
                    print(leet_word)

        # Append all number combinations word by word
        for combo in _number_combos(word):
            if len(combo) <= 14:
                combo_hash = _lm_encode(combo)
                rainbow_table[combo_hash] = combo
                print(combo)

    # Dump to create new file
    with open(output_file, 'w') as f:
        json.dump(rainbow_table, f, indent=4)

# Dictionary json that I found
dictionary = 'words_dictionary.json'

# Output file
output = 'rainbow_table.json'

generate_table(dictionary, output)
print("Rainbow table created")

# I had to create two json files,
# because I made the first one,
# and then I wanted to include for the extra credit,
# so I just combined the two

# This took probably almost a full 24 hours of run time to put together,
# but it was so worth it
