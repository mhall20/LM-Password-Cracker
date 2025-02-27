import json
import time # For timer

# I found a json file with all dictionary words and then turned that into my own rainbow table - https://github.com/dwyl/english-words
def _load_dictionary(file):
    """ Loads JSON word dictionary """
    with open(file, 'r') as file:
        return json.load(file)
    
# Extract just the LM from dump
def _get_password(password):
    """ Extracts LM hash from password"""
    parts = password.split(':')

    # Make sure password from dump is in correct format
    if len(parts) >3:
        return parts[2]
    return None

# At first, I would check every dictionary word and its number combination,
# but it would take hours to get the tallman password,
# so I created my own rainbow table to make the process way quicker
def password_crack(input_password, rainbow_table):
    """ Crack LM password """

    # Start the timer
    start_time = time.time()

    # Load the rainbow table I created
    table = _load_dictionary(rainbow_table)

    # Get the password from the provided dump
    password = _get_password(input_password)

    # If the password is in the table then yippee
    if password in table:
        word = table[password]

        # End timer and track time elapsed
        end_time = time.time()
        timer = end_time - start_time

        # Print in a nice format
        print(f"Password Cracked: {word.upper()} : {timer:.2f} seconds")
        return

    # If password not in the table the world will fall apart
    print("Password not found in dictionary")

# Run main
if __name__ == "__main__":

    # Import my json rainbow table
    rainbow = 'rainbow_table.json'

    # Import the pwdump and cycle through
    with open('pwdump.txt', 'r') as file:
        for line in file:
            password_crack(line, rainbow)