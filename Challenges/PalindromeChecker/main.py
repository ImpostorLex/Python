def is_palindrome(s):

    old = s.lower().replace(" ", "")
    new = s.lower().replace(" ", "")
    
    
    return old == new[::-1]
    
    
print(is_palindrome("level"))   
print(is_palindrome("Python"))    
print(is_palindrome("A man a plan a canal Panama"))  
