# B-Tree Algorithm Implementation in Python

See [wiki](https://en.wikipedia.org/wiki/B-tree).


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
