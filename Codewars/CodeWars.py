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


###########################################
#Challenge 4 Unique Code
###########################################

# Implement the function unique_in_order which takes as argument a sequence and returns a list of items without any elements with the same value next to each other and preserving the original order of elements.
# 
# For example:
# 
# unique_in_order('AAAABBBCCDAABBB') == ['A', 'B', 'C', 'D', 'A', 'B']
# unique_in_order('ABBCcAD')         == ['A', 'B', 'C', 'c', 'A', 'D']
# unique_in_order([1,2,2,3,3])       == [1,2,3]
def unique_in_order(iterable):
    pre_item = None
    result = []
    for item in iterable:
        if item != pre_item:
            result.append(item)
            pre_item = item  #important!!!
    return result


#############################################################################
# Challenge 5
# Delete occurrences of an element if it occurs more than n times
# Enough is enough!
#############################################################################
# Alice and Bob were on a holiday. Both of them took many pictures of the places they've been, and now they want to show Charlie their entire collection. However, Charlie doesn't like this sessions, since the motive usually repeats. He isn't fond of seeing the Eiffel tower 40 times. He tells them that he will only sit during the session if they show the same motive at most N times. Luckily, Alice and Bob are able to encode the motive as a number. Can you help them to remove numbers such that their list contains each number only up to N times, without changing the order?
# 
# Task
# 
# Given a list lst and a number N, create a new list that contains each number of lst at most N times without reordering. For example if N = 2, and the input is [1,2,3,1,2,1,2,3], you take [1,2,3,1,2], drop the next [1,2] since this would lead to 1 and 2 being in the result 3 times, and then take 3, which leads to [1,2,3,1,2,3].
# 
# Example
# 
#   delete_nth ([1,1,1,1],2) # return [1,1]
# 
#   delete_nth ([20,37,20,21],1) # return [20,37,21]

def delete_nth(order,max_e):
    result = []
    for char in order:
        if result.count(char) <max_e:
            result.append(char)
        else:
            pass
    return result 
print(delete_nth([20,37,20,21], 1))


#########################################
# Challenge 6 Consecutive strings
########################################## 
# You are given an array strarr of strings and an integer k. Your task is to return the first longest string consisting of k consecutive strings taken in the array.
# 
# #Example: longest_consec(["zone", "abigail", "theta", "form", "libe", "zas", "theta", "abigail"], 2) --> "abigailtheta"
# 
# n being the length of the string array, if n = 0 or k > n or k <= 0 return "".


def aaa(list, n):
    result = list[0:n]
    k = len(list)
    if k == 0 or n>k or n<=0:
        return ''
    else:
        for i in range(1,len(list)):
            x = ''.join(list[i:i+n])
            y = ''.join(result)
            if len(x) > len(y):
                result = list[i:i+n]
            else:
                pass
    return ''.join(result)
        
print(aaa(["zone", "abigail", "theta", "form", "libe", "zas"], 2))



##########################################
# Challenge 7 Simple Pig Latin 
##########################################
# Move the first letter of each word to the end of it, then add 'ay' to the end of the word.
# 
# pig_it('Pig latin is cool') # igPay atinlay siay oolcay


#This one is not so good, look at other solutions !!! 
# String.split() could be applied !
def pig_it(string):
    result = []
    new_result = []
    string = string.split()
    for char in string:
        x = list(char)
        y = x[1:len(x)]
        z = x[0:1]
        q = y+z
        result.append(q)
    for index in result:
        for xxxx in index:
            if xxxx.isalnum():
                m = index + ['a','y']
                m = ''.join(m)
            else: 
                m = index
                m = ''.join(m)
        new_result.append(m)
        result = ' '.join(new_result)
    return result


##########################################
# Challenge 8 Sum of pairs
##########################################
# Given a list of integers and a single sum value, return the first two values (parse from the left please) in order of appearance that add up to form the sum.
# 
# sum_pairs([11, 3, 7, 5],         10)
# #              ^--^      3 + 7 = 10
# == [3, 7]
# 
# sum_pairs([4, 3, 2, 3, 4],         6)
# #          ^-----^         4 + 2 = 6, indices: 0, 2 *
# #             ^-----^      3 + 3 = 6, indices: 1, 3
# #                ^-----^   2 + 4 = 6, indices: 2, 4
# #  * entire pair is earlier, and therefore is the correct answer
# == [4, 2]
# 
# sum_pairs([0, 0, -2, 3], 2)
# #  there are no pairs of values that can be added to produce 2.
# == None/nil/undefined (Based on the language)
# 
# sum_pairs([10, 5, 2, 3, 7, 5],         10)
# #              ^-----------^   5 + 5 = 10, indices: 1, 5
# #                    ^--^      3 + 7 = 10, indices: 3, 4 *
# #  * entire pair is earlier, and therefore is the correct answer
# == [3, 7]
# Negative numbers and duplicate numbers can and will appear.
# 
# NOTE: There will also be lists tested of lengths upwards of 10,000,000 elements. Be sure your code doesn't time out.


#原版，效率太差，无法通过
def sum_pairs(ints, s):
    x = len(ints)
    result = []
    for i in range(0, x):
        for z in range(0,i):
            if ints[i] + ints[z] == s:
                result = [ints[z], ints[i]]
                return result
    if len(result) == 0:
        return None

#网上找到的dict版本
def sum_pairs(ints, s):
    map = {}
    n = len(ints)
    index1 = n
    index2 = n
    checked = set()
    
    for i in range(n):
        map[ints[i]] = i
    
    m = n
    i = 0
    while i < m:
        num = ints[i]
        dif = s - num
        if dif in map and map[dif] != i and num not in checked:
            checked.add(dif)
            j = map[dif]
            if j < index2:
                index1 = i
                index2 = j
                m = j
        i += 1
    
    if index1 >= n or index2 >= n:
        return None
    
    return [ints[index1], ints[index2]]

#智商碾压版
def sum_pairs(lst, s):
    cache = set()
    for i in lst:
        if s - i in cache:
            return [s - i, i]
        cache.add(i)


        
##########################################
# Challenge 9 Parse HTML/CSS Colors
##########################################
# In this kata you parse RGB colors represented by strings. The formats are primarily used in HTML and CSS. Your task is to implement a function which takes a color as a string and returns the parsed color as a map (see Examples).
# 
# Input:
# 
# The input string represents one of the following:
# 
# 6-digit hexadecimal - "#RRGGBB"
# e.g. "#012345", "#789abc", "#FFA077"
# Each pair of digits represents a value of the channel in hexadecimal: 00 to FF
# 3-digit hexadecimal - "#RGB"
# e.g. "#012", "#aaa", "#F5A"
# Each digit represents a value 0 to F which translates to 2-digit hexadecimal: 0->00, 1->11, 2->22, and so on.
# Preset color name
# e.g. "red", "BLUE", "LimeGreen"
# You have to use the predefined map PRESET_COLORS (JavaScript, Python, Ruby), presetColors (Java, C#, Haskell), or preset-colors (Clojure). The keys are the names of preset colors in lower-case and the values are the corresponding colors in 6-digit hexadecimal (same as 1. "#RRGGBB").
# Examples:
# 
# parse_html_color('#80FFA0')   # => {'r': 128, 'g': 255, 'b': 160}
# parse_html_color('#3B7')      # => {'r': 51,  'g': 187, 'b': 119}
# parse_html_color('LimeGreen') # => {'r': 50,  'g': 205, 'b': 50 }

def parse_html_color(color):
    if color[0] == '#':
        if len(color) == 7:
            new_color = color[1:7]
            r = int(new_color[0:2],16)
            g = int(new_color[2:4],16)
            b = int(new_color[4:6],16)
        elif len(color) == 4:
            new_color = color[1:4]
            r = str(new_color[0])*2
            g = str(new_color[1])*2
            b = str(new_color[2])*2
            r = int(r,16)
            g = int(g,16)
            b = int(b,16)        
        return {'r' : r, 'g': g, 'b':b}
    else:
        color = color.lower()
        color = PRESET_COLORS[color]
        new_color = color[1:7]
        r = int(new_color[0:2],16)
        g = int(new_color[2:4],16)
        b = int(new_color[4:6],16)
    return {'r' : r, 'g': g, 'b':b}

# Use try to solve it much easier
def parse_html_color(color):
    try:
        color = PRESET_COLORS[color.lower()]
    except:
        pass
    if color[0] == '#' and len(color) == 7:
        return {'r': int(color[1:3], 16), 'g': int(color[3:5], 16), 'b': int(color[5:7], 16)}
    else:
        return {'r': int(color[1]*2, 16), 'g': int(color[2]*2, 16), 'b': int(color[3]*2, 16)}
    
    
  ##########################################
# Challenge 10 Tic-Tac-Toe Checker
##########################################
# If we were to set up a Tic-Tac-Toe game, we would want to know whether the board's current state is solved, wouldn't we? Our goal is to create a function that will check that for us!
# 
# Assume that the board comes in the form of a 3x3 array, where the value is 0 if a spot is empty, 1 if it is an X, or 2 if it is an O, like so:
# 
# [[0,0,1],
#  [0,1,2],
#  [2,1,0]]
# We want our function to return -1 if the board is not solved yet, 1 if X won, 2 if O won, or 0 if it's a cat's game (i.e. a draw).
# 
# You may assume that the board passed in is valid in the context of a game of Tic-Tac-Toe.
def isSolved(board):
  for i in range(0,3):
    if board[i][0] == board[i][1] == board[i][2] != 0:
      return board[i][0]
    elif board[0][i] == board[1][i] == board[2][i] != 0:
      return board[0][i]
      
  if board[0][0] == board[1][1] == board[2][2] != 0:
    return board[0][0]
  elif board[0][2] == board[1][1] == board[2][0] != 0:
    return board[0][0]

  elif 0 not in board[0] and 0 not in board[1] and 0 not in board[2]:
    return 0
  else:
    return -1
