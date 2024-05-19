import os
import pandas as pd
from persistence_methods import *
from persistence_process_queries import *

class PersistentStore():

    def __init__(self, query_order):
        self.table = {}                
        self.query_order = query_order  
        self.operator_list = {
            "equals": "==",
            "nequals": "!=",
            "lt": "<",
            "lte": "<=",
            "gt": ">",
            "gte": ">=",
        }

        self.boolean_list = {
            "and": "and",
            "or": "or",
            "not": "not"
        }

        # self.cross_operator = {"<":">=", ">":"<=", "<=":">", ">=":"<", "":"", "":""}

        self.variables = {}
        self.update_record = {}                

    def __del__(self):
        # print(self.table['data'])
        ...
    

PersistentStore.get_list_item = get_list_item
PersistentStore.table_list = table_list
PersistentStore.read_table = read_table
PersistentStore.post_query_order = post_query_order
PersistentStore.process_queries = process_queries
PersistentStore.store_variable = store_variable
PersistentStore.create_variable = create_variable
PersistentStore.update_liveness = update_liveness
PersistentStore.save_table = save_table
PersistentStore.cols_where = cols_where


if __name__ == "__main__":
    query_order = [{'url': 'data/zillow.csv', 'short_table_name': 'CUSTOMERS', 'header': 'False', 'type': 'import_table'}]
    persist_store = PersistentStore(query_order)
    persist_store.process_queries()