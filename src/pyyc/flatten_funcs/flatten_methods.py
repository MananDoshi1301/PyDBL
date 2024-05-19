import random 
import copy 

def pull_consts(self, n):
    lst = []
    for i in range(n):
        lst.append(self.stack.pop())

    if n == 1:
        return lst[0]
    return lst

def push_consts(self, lst):
    for i in lst:
        self.stack.push(i)

def query_order(self, key, value):
    self.order_dict[key] = value

def store_var(self, key, value):
    self.variables[key] = value

def generate_id(self):
    while True:
        unique_digits = random.sample(range(10), 4)
        number = int(''.join(map(str, unique_digits)))        
        if number not in self.generated_numbers:
            self.generated_numbers.add(number)            
            return number

def get_new_var_name(self):
    name = f"t_{self.generate_id()}_{self.counter}"
    self.counter += 1      
    return name

def add_flat_exp(self, lst):    
    self.flatExpr += lst

def get_query_order(self):
    return self.order_dict_list

def get_vars(self):
    return self.variables

def append_order_deepcopy(self):
    d2 = copy.deepcopy(self.order_dict)
    self.order_dict_list.append(d2)    
    self.order_dict.clear()