import ast
from ast import *
import os, sys
sys.path.insert(0, f'{os.getcwd()}/src/pyyc/flatten_funcs')
sys.path.insert(0, f'{os.getcwd()}/src/pyyc/persistence_funcs')
sys.path.insert(0, f'{os.getcwd()}/src/pyyc/non_persistence_funcs')

from flatten import PostfixVisitor
from assembly import Assembler
from persistence import PersistentStore
from non_persistence import NonPersistence
from query_separation import QuerySeparation
from non_persisting_assembly import NonPersistingAssembly

def ast_dev(expression):
    tree = ast.parse(expression)
    ast_tree = ast.dump(tree, indent = 4)
    # print(ast_tree)

class Compile():

    def __init__(self):
        self.tree = ""
        self.query_order = []
        self.IR = []

    def flatten(self, code):
        ####################### Lexing Parsing
        self.tree = ast.parse(code)

        ####################### Flattening
        postfix_visitor = PostfixVisitor()
        postfix_visitor.traverse(self.tree)
        self.query_order = postfix_visitor.get_query_order()
        # print(self.query_order)
        # print(postfix_visitor.get_vars())

    def optimization(self):
        ####################### Optimization and IR
        assm = Assembler(self.query_order)
        assm.IR_generation()
        self.IR = assm.IR        
        # for i in IR:
        #     print(i)
        # print("\n\n")

    def storage(self):
        ####################### Separation of Persistent, non-Persisten Queries
        query_seperator = QuerySeparation(self.IR)
        query_seperator.separate_queries()
        persistent_queries = query_seperator.get_persistent_queries()
        non_persistent_queries = query_seperator.get_non_persistent_queries()

        ####################### Calling Persistent and Non-Persistent        
        persist_store = PersistentStore(persistent_queries)
        persist_store.process_queries()

        non_persisting_assembly_channel = NonPersistingAssembly()
        non_persist_store = NonPersistence(non_persistent_queries, non_persisting_assembly_channel)
        non_persist_store.process_queries()

    def process_query(self, code):
        self.flatten(code)
        self.optimization()
        self.storage()


if __name__ == "__main__":
    
    code = """

############################################### IMPORT

# import_table(url="data/zillow.csv", table_name="zillow")
import_table(url="database/zillow_db", table_name="zillow")


############################################### SELECT
select(['*'], table="zillow")
# select(['Zip'], table="zillow")
# select(['Beds', "Baths"], table="zillow", orderBy=('Beds', 'DESC'))

# cond1 = {">" : ("Beds", 3)}
# cond2 = {">" : ("Baths", 3)}
# cond3 = {"or" : (cond1, cond2)}
# cond4 = {"==": ("Index", 3)}
# select(['Beds', "Baths"], table="zillow", where = (cond3), orderBy=('Beds', 'DESC'))

# select(['col1', 'col2'], table="zillow")
# select(["col1", "col2"], table="zillow", where=(condition3))


############################################### UPDATE
# set_cond = {"=": ("Year", "2001")}
# where_cond = {">": ("Beds", 3)}
# update(set = (set_cond), table="zillow")
# update(set = (set_cond), table="zillow", where = (where_cond))


############################################### DELETE
# cond1 = {"<=" : ("Beds", 3)}
# delete(table="zillow", where=(cond1))
# delete(table="zillow")

############################################### INDEX
# index(['Index'], index_name="short_customer", table="zillow")
# select(['Beds', "Baths"], table="zillow", where = (cond4))
# index(['*'], index_name="short_customer", table="zillow")

############################################### hset
# hset('a', 1)
# hset('b', 2)
# hset('c', 3)
# hset('d', 4)
# hget('b')
# hset('e', 5)
# hget('c')
# hset('f', 6)
# hget('d')
# hset('g', 7)
# hget('e')
"""
    
    ast_dev(code)      
    co = Compile()
    co.process_query(code)
