# Challenge 2 - Find out the most frequently letter

# My solution
def checkio(text):
    text = text.lower()
    text_l = list(text)
    text_s = sorted(set(text_l))
    m = 0
    dic = {}
    for ch in text_s:
        if ch.isalpha():
            count = text_l.count(ch)
            dic[ch] = count
            m = max(count, m)
    for key, value in dic.items():
        if value == m:
            return key

# Best solution
import string
def checkio(text):
    text = text.lower()
    max(string.ascii_lowercase, key = text.count)
# max run to find the largest value in a iterable object by key text.count and return the letter
