# B-Tree Algorithm Implementation in Python

The implementation of the B-Tree data structure and its adjacent algorithms for insertion, deletion, and searching
follows the description from the following source:

Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, and Clifford Stein. 2009. Introduction to Algorithms,
Third Edition (3rd. ed.). The MIT Press. Chapter 18, pp. 484-504.


## Usage

0. Get [uv](https://github.com/astral-sh/uv)

1. Run a Python shell:

```bash
uv run ipython
```

2. Experiment:

```python
import btree

b = btree.BTree(degree=2)
for i in range(10):
    b.insert(i)
    
print(b)
b.search(9)
b.delete(7)
print(b)
```


## Development

```bash
make
```
