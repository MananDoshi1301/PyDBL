import copy

def var_creator(self, cmd, node = None):    

    if cmd == "keyword":        
        parameter = self.pull_consts(1)   
        # print("###########", parameter)
                
        if parameter == "table":
            # table_type = Constant
            table_type, table_name = self.pull_consts(2)
            self.query_order("table_name", f"{table_name}")                    

        elif parameter == "set":
            # self.stack.iterate()
            set_variable, set_type = self.pull_consts(2)
            print("-----------", self.stack.iterate())
            # print(set_type, set_variable)
            temp = set_variable
            while temp in self.variables:
                temp = self.variables[temp]
            self.query_order("set", f"{temp}")

        elif parameter == "where":
            condition, condition_type = self.pull_consts(2)
            self.query_order("where", f"{condition}")

        elif parameter == "header":
            header_type, header = self.pull_consts(2)
            self.query_order("header", header)

        elif parameter == "table_name":
            table_type, table = self.pull_consts(2)
            self.query_order("table_name", table)

        elif parameter == "url":
            url_type, url = self.pull_consts(2)
            self.query_order("url", url)

        elif parameter == "orderBy":            
            var1, var1_type = self.pull_consts(2)
            var2, var2_type = self.pull_consts(2)
            if var1_type == "Load" and var2_type == "Load":
                self.query_order("orderBy", (var2, var1))

        elif parameter == "index_name":
            index_type, index_name = self.pull_consts(2)
            self.query_order("index_name", index_name)


            
        else:
            self.push_consts([parameter])

        # print(self.order_dict)  

    elif cmd == "hset":
        val_type, val, var_type, var, operation, op_type = self.pull_consts(6)
        
        if operation == "hset" and op_type == "Load":
            if val_type == "Constant" and var_type == "Constant":
                self.store_var(var, val)
                self.query_order('type', 'hset')
                self.query_order('key', var)
                self.query_order('value', val)
                self.append_order_deepcopy()

    elif cmd == "hget":
        var_type, var, operation, op_type = self.pull_consts(4)        
        if operation == "hget" and op_type == "Load":
            if var_type == "Constant":                
                self.query_order('type', 'hget')
                self.query_order('key', var)                
                self.append_order_deepcopy()                

    elif cmd == "Call":
        parameter = ""
        parameter, parameter_type = self.pull_consts(2)
        # print(parameter, parameter_type)
        if parameter_type == "Load":
            if parameter == "select":                
                self.query_order('type', 'select')                

            elif parameter == "update":                
                self.query_order('type', 'update')   

            elif parameter == "delete":             
                self.query_order('type', 'delete')

            elif parameter == "import_table":             
                self.query_order('type', 'import_table')
                if "header" not in self.order_dict:
                    self.query_order('header', 'True')

            elif parameter == "index":             
                self.query_order('type', 'index')   
            
            if self.flatExpr:
                d1 = copy.deepcopy(self.flatExpr)
                self.order_dict_list.append({'type': 'flat_block', 'flat_expr': d1})    
                self.flatExpr.clear()
            
            self.append_order_deepcopy()

        else:
            self.push_consts([parameter_type, parameter])

    elif cmd == "List":
        operation_type = ""
        operation_type = self.pull_consts(1)

        if operation_type == "Load":
            total_params = len(node.elts)
            select_list = []
            for i in range(total_params):
                column_type, column = self.pull_consts(2)
                select_list.insert(0, column)
            self.query_order('select', select_list)

    elif cmd == "Tuple":
        node_type = self.pull_consts(1)
        if self.stack.top() != "Constant":
            a, a_type, b, b_type = self.pull_consts(4)
            self.push_consts([b, b_type, a, a_type])

        if node_type == "Load":
            val_type, val = self.pull_consts(2)
            table_type, table = self.pull_consts(2)
            # new_var_name_1 = self.get_new_var_name()
            # new_var_name_2 = self.get_new_var_name()
            # self.store_var(new_var_name_1, table)
            # self.store_var(new_var_name_2, val)
            # self.add_flat_exp([f"{new_var_name_1} = {table}", f"{new_var_name_2} = {val}"])
            self.push_consts(['Load', table, 'Load', val])

    elif cmd == "Dict":
        b, b_type, a, a_type = self.pull_consts(4)
        operator_type = self.pull_consts(1)
        
        if operator_type == "Constant":
            operator = self.pull_consts(1)
            if operator in self.operator_list or operator in self.boolean_list:
                # new_var_name = self.get_new_var_name()
                string = f"{a} {operator} {b}"
                # first_name = Alfred

                # self.store_var(new_var_name, string)
                # self.add_flat_exp([f"{new_var_name} = {string}"])
                # print("####", new_var_name)
                # self.push_consts(['Load', new_var_name])
                self.push_consts(['Load', string])
            elif operator in self.set_conditional_operator:
                print("##################", a, operator, b)
                string = f"{a} {operator} {b}"
                self.push_consts(['Load', string])
    
    elif cmd == "Assign":
        to_store, store_type = self.pull_consts(2)            
        var_name, operation_type = self.pull_consts(2)

        if operation_type == "Store":
            self.store_var(var_name, to_store)
            self.add_flat_exp([f"{var_name} = {to_store}"])