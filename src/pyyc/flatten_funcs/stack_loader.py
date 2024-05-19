def stack_loader(self, node):
    name_type = type(node).__name__        
    
    if name_type == 'Assign':
        # Always a variable assignment 
        self.var_creator(name_type)

    elif name_type == 'keyword':   
        keyword_type = ["table", "set", "where", "header", "table_name", "url", "column", "orderBy", "index_name"]
        if (node.arg and node.arg in keyword_type):                 
            self.var_creator(name_type)

    elif name_type == 'Name':      
        # node, node_type = self.pull_consts(2)
        # if b == "Load":              
        self.var_creator(name_type)

    ## select, update, delete, index 
    elif name_type == 'Call':       
        if type(node.func).__name__ == "Name" and node.func.id == "hset":
            # print(node.func.id)
            self.var_creator('hset')    
        elif type(node.func).__name__ == "Name" and node.func.id == "hget":
            self.var_creator('hget')    
        else:            
            self.var_creator(name_type)            
    
    elif name_type == 'Tuple':                    
        self.var_creator(name_type)

    elif name_type == 'List':                    
        self.var_creator(name_type, node)  

    elif name_type == 'Dict':                    
        self.var_creator(name_type)            
        
    elif name_type == 'Expr':
        self.var_creator(name_type)

    else:
        self.stack.push(name_type)
    # self.stack.iterate()