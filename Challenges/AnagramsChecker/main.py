def are_anagrams(s1, s2):
    
    new_s2 = list(s2.replace(" ", ""))
    s1 = s1.replace(" ", "")
    flag = False
    
    
    for letter in s1:
        if letter in new_s2:
            # Remove first occurance.
            new_s2.remove(letter)
            flag = True
        else:
            flag = False
            break
    
    return flag
            
print(are_anagrams("listen", "silent"))    # True
print(are_anagrams("hello", "world"))       # False
print(are_anagrams("debit card", "bad credit"))    # True
