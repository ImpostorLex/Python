
def median_calculator(arr):
    
    arr.sort()
    
    total = sum(arr)
    median = total / len(arr)
    
    return f"The array of {arr} has a median of {median}"
    

arr1 = [1,2,3,4,5]
arr2 = [5,4,2,1,7]


print(median_calculator(arr1))
print(median_calculator(arr2))






