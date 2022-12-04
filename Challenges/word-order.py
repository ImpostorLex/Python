# Explanation : https://www.hackerrank.com/challenges/word-order/problem?isFullScreen=true

n_of_strings = int(input("How many words you want to enter? "))
list_of_strings = []
is_word_same = []
dict = {}
ctr = 0
mock_list = []
placeholder = ""

for x in range(0, n_of_strings):
    user_input = input(f"Enter word {x + 1}: ")

    if user_input not in is_word_same:
        dict[user_input] = 1
        is_word_same.append(user_input)
        

    elif user_input in is_word_same:
        dict_value = dict[user_input]
        dict[user_input] = 1 + dict_value
        dict_value = 0

x = str(list(dict.values())).strip("[]").strip(",")
print(f"{len(is_word_same)}\n{x}")
                
            




    







        



        




   


        





    



