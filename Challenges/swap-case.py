
# Swap case a string  hello WORLD should output
swap_case = ""
user_input = input("Enter a string: ")

for letter in user_input:

    if letter.isupper():
        swap_case += letter.lower()

    elif letter.islower():
        swap_case += letter.upper()

    else:
        swap_case += letter

print(swap_case)


