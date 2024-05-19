import pandas as pd

def get_list_item(self, lst, idxs):
    res = []
    for i in idxs:
        res.append(lst[i])
    
    if len(res) == 1:
        return res[0]
    return res

def table_list(self):
    for k, v in self.table.items():
        print(k, end = "..")

def read_table(self, url = ""):
    if url:
        # try:
        #     url = url.split('.')
        #     db = url[0]+'_db'
        #     print(db)
        #     table = pd.read_csv(db)
        # except:
        #     table = pd.read_csv(url)
        table = pd.read_csv(url)
            
        table.columns = table.columns.str.replace('"', '')
        table.columns = [i.strip() for i in table.columns]
        return table            

def save_table(self, df, name = ""):
    try:
        df.to_csv(name+"_db")
    except:
        print("Internal Server Error. File not Saved :(")

def post_query_order(self, query_order = ""):
    self.query_order = query_order

def store_variable(self, key, value):
    self.variables[key] = value

def create_variable(self, query):
    operator = self.get_list_item(query, [0])    

    if operator in self.operator_list:
        col_name, value, var_name = self.get_list_item(query, range(1, len(query)))
        # d = {'col_name': col_name, }        
        self.store_variable(var_name, f"{col_name} {self.operator_list[operator]} {value}")

        if var_name in self.update_record:
            self.update_record[var_name] = {'col_name': col_name, 'value': value, 'operator': self.operator_list[operator]}
            # self.update_record[var_name] = {'cond': f"df[{col_name}] {self.operator_list[operator]} {value}", 'col_name': col_name}


    elif operator in self.boolean_list:
        cond1, cond2, var_name = self.get_list_item(query, range(1, len(query)))
        
        temp1 = cond1
        while temp1 in self.variables:
            temp1 = self.variables[temp1]

        temp2 = cond2
        while temp2 in self.variables:
            temp2 = self.variables[temp2]

        self.store_variable(var_name, f"{temp1} {self.boolean_list[operator]} {temp2}")    

def update_liveness(self):
    query_order = self.query_order       
    for i in range(len(query_order) - 1, -1, -1):
        query = query_order[i]        
        query_type = self.get_list_item(query, [0])
        if query_type == 'update':            
            update_where = self.get_list_item(query,[len(query) - 1])            
            if update_where:
                self.update_record[update_where] = ""
