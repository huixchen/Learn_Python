```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#http://blog.xiayf.cn/2013/03/30/argparse/
#https://blog.ixxoo.me/argparse.html

from PIL import Image
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('file')
parser.add_argument('-o', '--output')
parser.add_argument('--width', type = int, default = 80)
parser.add_argument('--height', type = int, default = 80)

args = parser.parse_args()

IMG = args.file
WIDTH = args.width
HEIGHT = args.height
OUTPUT = args.output

ascii_char = list("$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. ")

def get_char(r,g,b,alpha=256):
    if alpha == 0:
        return ''
    length = len(ascii_char)
    gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b)

    unit = (256.0 + 1)/length
    return ascii_char[int(gray/unit)]

if __name__ == '__main__':
    im = Image.open(IMG)
    im = im.resize((WIDTH, HEIGHT), Image.NEAREST)

    txt = ""

    for i in range(HEIGHT):
        for j in range(WIDTH):
            txt += get_char(*im.getpixel((j,i)))
        txt += '\n'
    print(txt)

    ####
    if OUTPUT:
        with open(OUTPUT, 'w') as f:
            f.write(txt)

    else:
        with open("output.txt", 'w') as f:
            f.write(txt)
```
## Argparse
argparse, as indicated by the name, it parse the arguments that we type into commind line. `add_argument()` is one function of `argparse.ArgumentParser`.
The function assign feature to the arguments.
For instance
```python
parser.add_argument('-o', '--output')
```
Above we added one optional arguments. `'-o'` is the argument's short name, while `'--output'` is the full name. When there are both full name and short name, the argument would be stored with the full name.
```python
parser.add_argument('file')
```
In contrast, above we called one compulsory argument called `file`
```python
parser.add_argument('--width', type = int, default = 80)
```
We can also define the args' type and default value as we state above.
Besides, we can decide range of the argument we want user to type in:
```python
parser.add_argument('--mode', choices=('read-only', 'read-write'))
```

Reference Link:
1. [http://blog.xiayf.cn/2013/03/30/argparse/](http://blog.xiayf.cn/2013/03/30/argparse/)
2. [https://blog.ixxoo.me/argparse.html](https://blog.ixxoo.me/argparse.html)

## PIL
`getpixel()` would find the RGBA value of the point we want to have. Value should be passed in is a tuple `(j,i)`. We used `*` in front of `getpixel()` to say that the returned value correspond to the `r,g,b,alpha` value of `get_char` function.

Reference Link:
1. [http://python3-cookbook.readthedocs.io/zh_CN/latest/c01/p02_unpack_elements_from_iterables.html](http://python3-cookbook.readthedocs.io/zh_CN/latest/c01/p02_unpack_elements_from_iterables.html)
