"""
The implementation of the B-Tree data structure and its
adjacent algorithms for insertion, deletion, and searching
follows the description from the following source:

Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, and Clifford Stein.
2009. Introduction to Algorithms, Third Edition (3rd. ed.). The MIT Press.
Chapter 18, pp. 484-504.
"""

import typing

ComparableT = typing.TypeVar("ComparableT", bound="Comparable", contravariant=True)


class Comparable(typing.Protocol[ComparableT]):
    def __lt__(self, other: ComparableT) -> bool: ...
    def __le__(self, other: ComparableT) -> bool: ...
    def __gt__(self, other: ComparableT) -> bool: ...
    def __ge__(self, other: ComparableT) -> bool: ...


class Node(typing.Generic[ComparableT]):
    """
    A node in the BTree.
    Can be either a root node, an internal node or a leaf node.

    Type hints:
    use class type for generic Node like this:
    >>> n: Node[int] = Node()
    """

    def __init__(self, is_leaf: bool = True):
        self.keys: list[ComparableT] = []
        self.children: list[Node] = []
        self.is_leaf: bool = is_leaf

    def __repr__(self) -> str:
        if self.is_leaf:
            return f"<LeafNode {self.keys}>"
        return f"<Node {self.keys}>"


class BTree(typing.Generic[ComparableT]):
    def __init__(self, degree: int):
        """
        Tree initialisation.

        :param degree: a **minimum** degree of the tree, i.e. the following must hold true:
          - Every internal node must have between (degree - 1) and (2 * degree - 1) keys
          - A root node can have fewer as (degree - 1) keys, but at least 1
          - An internal node must have between (degree) and (2 * degree) children

        Type hinting:
        use class type for generic BTree like this:
        >>> b_int: BTree[int] = BTree(degree=2)
        >>> b_int.insert(1)
        >>> b_str: BTree[str] = BTree(degree=2)
        >>> b_str.insert("a")
        """
        assert degree >= 2, "Minimum degree of the BTree must be at least 2"
        self.degree: int = degree
        self.root: Node = Node()

    def _search(self, key: ComparableT, node: Node) -> tuple[Node, int] | None:
        # Find the smallest index of the key that is less or equal to the target key
        position = 0
        while position < len(node.keys) and key > node.keys[position]:
            position += 1

        # If the key at the position is equal to the target key, return the node and position of the key
        if position < len(node.keys) and key == node.keys[position]:
            return node, position

        # Key is not found so far and the node is a leaf node,
        # i.e. there's no more child nodes to search in, stop searching.
        if node.is_leaf:
            return None

        # Recur within the right child node
        return self._search(key, node.children[position])

    def search(self, key: ComparableT) -> tuple[Node, int] | None:
        """
        Search for a given key in the tree and if found return a Node that contains it
        along with the key's position in the Node. If the key is not found return None.
        """
        return self._search(key=key, node=self.root)

    def is_node_full(self, node: Node) -> bool:
        return len(node.keys) == (2 * self.degree) - 1

    def insert(self, key: ComparableT) -> None:
        """
        Insert a given key into the tree.
        """
        if self.is_node_full(self.root):
            # If a node is full, it must be split.
            # The tree's height is increased by 1 in this case.
            new_root: Node = Node(is_leaf=False)
            new_root.children.append(self.root)
            # Split the old root into two nodes and move the middle key up to the new root.
            self._split_child(parent=new_root, position=0)
            self.root = new_root

        self._insert_into_non_full_node(self.root, key)

    def _insert_into_non_full_node(self, node: Node, key: ComparableT) -> None:
        """
        Insert a key into a node that is guaranteed to be non-full
        """
        # Starting at the last key of the node
        position = len(node.keys) - 1
        # Inserting into a leaf node
        if node.is_leaf:
            # Add a stub for the new key
            node.keys.append(0)
            while position >= 0 and key < node.keys[position]:
                # Shifting larger keys 1 position to the right
                node.keys[position + 1] = node.keys[position]
                position -= 1
            # Insert the key at the correct position
            node.keys[position + 1] = key
        else:
            # Inserting into an internal node
            while position >= 0 and key < node.keys[position]:
                position -= 1
            position += 1

            # If the found child is full, split it before inserting.
            # Split will also update the parent and move the middle key up.
            if self.is_node_full(node.children[position]):
                self._split_child(node, position)
                if key > node.keys[position]:
                    # This guarantees that the recursion below never descents to the full node,
                    # so the algorithm terminates.
                    position += 1
            self._insert_into_non_full_node(node.children[position], key)

    def _split_child(self, parent: Node, position: int) -> None:
        """
        Split a full child of the parent node at the given position.
        """
        child = parent.children[position]
        new_child: Node = Node(is_leaf=child.is_leaf)

        # A full node has (2 * degree - 1) keys,
        # so the position at (degree - 1) is the middle one.
        # Move the middle key from the child to the parent.
        parent.keys.insert(position, child.keys[self.degree - 1])
        parent.children.insert(position + 1, new_child)

        # Split the keys and children between the old and new child nodes.
        # Last (degree - 1) keys go to the new child.
        new_child.keys = child.keys[self.degree :]
        # First (degree - 1) keys remain in the old child.
        child.keys = child.keys[: self.degree - 1]

        # If the node is an internal node, its (2 * degree) children
        # are also split between the two new nodes.
        if not child.is_leaf:
            new_child.children = child.children[self.degree :]
            child.children = child.children[: self.degree]

    def delete(self, key: ComparableT) -> None:
        """
        Delete a key from the tree
        """
        self._delete(self.root, key)
        # If after deletion the root node has no keys, shrink the height of the tree by 1.
        if len(self.root.keys) == 0 and not self.root.is_leaf:
            self.root = self.root.children[0]

    def _delete(self, node: Node, key: ComparableT) -> None:
        position = 0
        while position < len(node.keys) and key > node.keys[position]:
            position += 1

        if position < len(node.keys) and node.keys[position] == key:
            if node.is_leaf:
                node.keys.pop(position)
            else:
                self._delete_from_internal_node(node, position)
        # The key is not found in the current node, go deeper
        elif not node.is_leaf:
            # If needed, fix a node with the shortage
            if len(node.children[position].keys) < self.degree:
                position = self._fill_node_with_shortage(node, position)
            self._delete(node.children[position], key)

    def _delete_from_internal_node(self, node: Node, position: int) -> None:
        key = node.keys[position]
        if len(node.children[position].keys) >= self.degree:
            predecessor_key: ComparableT = self._get_predecessor_key(
                node.children[position]
            )
            node.keys[position] = predecessor_key
            self._delete(node.children[position], predecessor_key)
        elif len(node.children[position + 1].keys) >= self.degree:
            successor_key: ComparableT = self._get_successor_key(
                node.children[position + 1]
            )
            node.keys[position] = successor_key
            self._delete(node.children[position + 1], successor_key)
        else:
            self._merge(node, position)
            self._delete(node.children[position], key)

    def _fill_node_with_shortage(self, parent: Node, position: int) -> int:
        """
        Balance the node so that it has `degree` keys, return updated position.
        """
        if position > 0 and len(parent.children[position - 1].keys) >= self.degree:
            self._borrow_from_prev(parent, position)
        elif (
            position < len(parent.children) - 1
            and len(parent.children[position + 1].keys) >= self.degree
        ):
            self._borrow_from_next(parent, position)
        else:
            if position < len(parent.children) - 1:
                self._merge(parent, position)
            else:
                self._merge(parent, position - 1)
                position -= 1

        return position

    def _merge(self, parent: Node, position: int) -> None:
        """
        Merge the child at given position with its right sibling and move the parent’s key down
        """
        child = parent.children[position]
        sibling = parent.children[position + 1]
        # Move parent's key down to the child
        child.keys.append(parent.keys.pop(position))
        # Merge sibling's keys into the child
        child.keys.extend(sibling.keys)
        if not child.is_leaf:
            child.children.extend(sibling.children)

        # Remove the sibling from parent
        parent.children.pop(position + 1)

    def _borrow_from_prev(self, parent: Node, position: int) -> None:
        """
        Borrow the key from previous sibling
        """
        child = parent.children[position]
        sibling = parent.children[position - 1]
        child.keys.insert(0, parent.keys[position - 1])
        if not sibling.is_leaf:
            child.children.insert(0, sibling.children.pop())
        parent.keys[position - 1] = sibling.keys.pop()

    def _borrow_from_next(self, parent: Node, position: int) -> None:
        """
        Borrow the key from next sibling
        """
        child = parent.children[position]
        sibling = parent.children[position + 1]
        child.keys.append(parent.keys[position])
        if not sibling.is_leaf:
            child.children.append(sibling.children.pop(0))
        parent.keys[position] = sibling.keys.pop(0)

    def _get_predecessor_key(self, node: Node):
        # Predecessor is the largest key in the left subtree
        while not node.is_leaf:
            node = node.children[-1]
        return node.keys[-1]

    def _get_successor_key(self, node):
        # Successor is the smallest key in the right subtree
        while not node.is_leaf:
            node = node.children[0]
        return node.keys[0]

    def _walk_tree(self, node: Node, level: int = 0, result: str = "") -> str:
        """
        Return a string representation of the tree starting from the given node.
        """
        offset = "  " * level
        result += f"{offset}{node}\n"
        for child in node.children:
            result = self._walk_tree(child, level + 1, result)
        return result

    def __repr__(self) -> str:
        return self._walk_tree(node=self.root)
