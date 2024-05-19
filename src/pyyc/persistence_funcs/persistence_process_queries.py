import pandas as pd
from index_tree import *
from copy import deepcopy

def cols_where(self, where):
    # reads condition and tells if the condition is on a specific column
    where = self.variables[where]
    cond_ls = where.split(" ")
    if len(cond_ls) > 3:
        return False, False, False
    else:
        return cond_ls[0], cond_ls[1], cond_ls[2]

def process_queries(self):
    self.update_liveness() 

    for i in self.query_order:
        query = i
        # print(query)                        

        if len(query) > 0:

            query_type = self.get_list_item(query, [0])

            if query_type == "create_table":
                name, url = self.get_list_item(query, [1, 2])                                        
                self.table[name] = self.read_table(url)
                # self.table_list()

            elif len(self.table) > 0:
                # Creating variables
                if query_type in self.operator_list or query_type in self.boolean_list:
                    self.create_variable(query)
                    # print(self.variables)

                elif query_type == "select":
                    col_list, table_name, where, order_by = self.get_list_item(query, range(1, len(query)))                    
                    if table_name in self.table:

                        if col_list:
                            
                            # Indexing
                            # with open('index/index_dict.pkl', 'rb') as f:
                            #     try:
                            #         index_table = pickle.load(f)
                            #     except EOFError:
                            #         index_table = {}
                            # if where and where in self.variables:
                            #     col, cond, val = self.cols_where(where)
                            #     print(col, "column")
                            #     print(index_table)
                            #     if col:
                            #     # find column in where  
                            #         for k, v in index_table.items():
                            #             if v == ([col], table_name):
                            #                 tree = build_index(k)
                            #                 df, table, all_cols_flag = {}, self.table[table_name], False
                            #                 print("GOT INDEX")
                            #         # now search in index rn
                            #                 if cond == "==":
                            #                     result = pickle.loads(tree[int(val)])
                            #                     print(result)
                            #     else:
                            df, table, all_cols_flag = {}, self.table[table_name], False                                
                            
                            for i in col_list:
                                if i == "*":
                                    df = table
                                    all_cols_flag = True
                                    flag = True
                                    break
                                else:
                                    # Add only certain columns
                                    df[i] = table.loc[:, i]
                            # df formation
                            if all_cols_flag == False:
                                df = pd.DataFrame(df)

                            if where and where in self.variables:                               
                                df = df.query(self.variables[where])

                            if order_by:
                                order_col, order_type = order_by                                
                                order = True if order_type == 'ASC' else False                                
                                df = df.sort_values(by = order_col, ascending = order)

                            print(df)

                elif query_type == "delete":
                    where, table_name = self.get_list_item(query, range(1, len(query)))
                    df = self.table[table_name]
                    filtered_df = None
                    if not where:
                        # delete whole table
                        # remove from memory
                        filtered_df = df.head(0)
                        ...
                    else:                        
                        cond = self.variables[where]
                        # print(df, "\n\n", cond)                        
                        condition_df = df.query(f'not {cond}')  
                        filtered_df = condition_df

                    print(filtered_df)
                    self.table[table_name] = filtered_df
                    self.save_table(filtered_df, table_name)

                elif query_type == "index":
                    cols, table_name, index_name = query[1], query[2], query[3]

                    with open("index/index_dict.pkl", 'rb') as f:
                        try:
                            index_table = pickle.load(f)
                        except EOFError:
                            index_table = {}

                    index_table[index_name] = (cols, table_name)
                    # print(index_table, "INDEX TABLE")
                    with open("index/index_dict.pkl", 'wb') as f:
                        pickle.dump(index_table, f)
                    
                    # print(cols, table_name)
                    all_cols_flag = False
                    if '*' in cols:
                        all_cols_flag = True
                    tree = build_index(index_name)
                    df = deepcopy(self.table[table_name]) # make index of first column
                    keys = df.loc[:, cols[0]].tolist()
                    kv = []
                    df.set_index(cols[0], inplace=True)
                    for k in keys:
                        r = pickle.dumps(df.loc[k].tolist())
                        tree.insert(k, r)
                    #made index
                    # for i in range(1, 10):
                    #     print(pickle.loads(tree[i]))

                elif query_type == "update":
                    where, set_value, table_name = self.get_list_item(query, [len(query) - 1, 1, 2])
                    df = self.table[table_name]
                    set_value = set_value.split(" ")            

                    if where:
                        record = self.update_record[where]
                        upd_col_name = record['col_name']
                        
                        df[upd_col_name] = df[upd_col_name].mask((eval("df[upd_col_name] " + record['operator'] + str(record['value']))), set_value[2])


                    else:
                        df[set_value[0]] = set_value[2]

                    print(df)
                    self.table[table_name] = df
                    self.save_table(df, table_name)
                    ...

