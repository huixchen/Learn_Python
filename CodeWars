###############################
# Challenge 1
###############################

# Create a function named divisors that takes an integer and returns an array with all of the integer's divisors(except for 1 and the number itself). If the number is prime return the string '(integer) is prime' (use Either String a in Haskell).
# 
# Example:
# 
# divisors(12); #should return [2,3,4,6]
# divisors(25); #should return [5]
# divisors(13); #should return "13 is prime"

def divisors(integer):
    result = []
    for i in range (2, integer-1):
        if integer % i == 0:
            result.append(i)
        else:
            pass
    if result == []:
        return str(integer) + ' is a prime'
    else:   
        return result
print(divisors(13))


###############################
# Build Tower
###############################
# Build Tower by the following given argument:
# number of floors (integer and always greater than 0).
# 
# Tower block is represented as *
# 
# Python: return a list;
# JavaScript: returns an Array;
# C#: returns a string[];
# PHP: returns an array;
# C++: returns a vector<string>;
# Haskell: returns a [String];
# Have fun!
# 
# for example, a tower of 3 floors looks like below
# 
# [
#   '  *  ', 
#   ' *** ', 
#   '*****'
# ]
# and a tower of 6 floors looks like below
# 
# [
#   '     *     ', 
#   '    ***    ', 
#   '   *****   ', 
#   '  *******  ', 
#   ' ********* ', 
#   '***********'
# ]

# My solution 
def tower_builder(n_floors):
    x = int(n_floors)
    result = []
    for i in range (1, n_floors+1):
        n = (x-i) * ' '+(2*i-1) * '*'+(x-i) * ' ' 
        result.append(n)
    return result

# One better solution 
def tower_builder(n):
    return[('*'*(2i-1)).center(n*2-1) for i in range(1, n+1)]
    
###########################################
#Challenge 3
###########################################
# In the following 6 digit number:
# 
# 283910
# 91 is the greatest sequence of 2 digits.
# 
# Complete the solution so that it returns the largest five digit number found within the number given.. The number will be passed in as a string of only digits. It should return a five digit integer. The number passed may be as large as 1000 digits.
# 
# Adapted from ProjectEuler.net
def largest(string):
    string = str(string)
    result = []
    for i in range (0, len(string)-4):
        x = string[i:i+5]
        x = int(x)
        result.append(x)
    return max(result)

print(largest(299999999))
