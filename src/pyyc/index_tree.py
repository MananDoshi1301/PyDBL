from bplustree import BPlusTree
import pickle
import os

# tree = BPlusTree('../bplustree.db', order=50)
# val = pickle.dumps({"hi": 1})
# tree[1] = val
# print(pickle.loads(tree[1]))

def build_index(index_name):
    index_loc = f'./index/{index_name}.db'
    tree = BPlusTree(index_loc, order=5)
    return tree

def delete_index(index_name):
    index_loc = f'./index/{index_name}.db'
    try:
        os.remove(index_loc)
    except e as Exception:
        print("Could not delete index")
