import ast
import os
from ast import *
from stack import Stack
from flatten_methods import *
from var_creator import *
from stack_loader import *

class PostfixVisitor(ast.NodeVisitor):

    def __init__(self):
        # Main operation stack
        self.stack = Stack()  

        # All k, v for select, update, delete, index, import             
        self.order_dict = {}

        # Storing query order for order_dict
        self.order_dict_list = []          

        # All variables 
        self.variables = {}

        # Utility function
        self.counter = 0
        self.generated_numbers = set()    
        self.operator_list = ["==", "!=", "<=", ">=", "<", ">"]
        self.boolean_list = ["and", "or"]
        self.set_conditional_operator = ["="]

        # flatExpr
        self.flatExpr = []
        

    def __del__(self):
        # print(self.variables)        
        # print(self.order_dict_list)
        for i in self.order_dict_list:
            print(i)
            ...
        ...

    def traverse(self, node):
        # Traverse left subtree first and the right 
        for child in ast.iter_child_nodes(node):            
            self.traverse(child)            
        self.visit(node)

    def visit(self, node):          
        name_type = type(node).__name__
        print(name_type)
        try:
            if (node.value == 0 or node.value) and isinstance(node.value, (str, int)):                  
                print("type:", type(node.value), node.value)              

                self.stack.push(node.value)                
        except:
            ...

        try:
            if (node.arg == 0 or node.arg):                
                self.stack.push(node.arg)                
        except:
            ...
                    
        try:
            if node.id:
                avoid_list = ["eval", "input"]                
                if node.id not in avoid_list:
                    self.stack.push(node.id)
        except:
            ...

        self.stack_loader(node)     
    ...

PostfixVisitor.stack_loader = stack_loader
PostfixVisitor.var_creator = var_creator
PostfixVisitor.pull_consts = pull_consts
PostfixVisitor.query_order = query_order
PostfixVisitor.push_consts = push_consts
PostfixVisitor.store_var = store_var
PostfixVisitor.get_new_var_name = get_new_var_name
PostfixVisitor.generate_id = generate_id
PostfixVisitor.add_flat_exp = add_flat_exp
PostfixVisitor.get_query_order = get_query_order
PostfixVisitor.get_vars = get_vars
PostfixVisitor.append_order_deepcopy = append_order_deepcopy

if __name__ == "__main__":
    po = PostfixVisitor()