import ast
from ast import *
from copy import deepcopy
from collections import defaultdict

class Assembler:
    def __init__(self, flat_code):
        self.flat_code = flat_code
        self.var_dict = {}
        self.IR = []  #will store only optimal commands
        self.IR_view = [] # needs to store what to show after making optimal disk calls
        self.view_to_IR = defaultdict(list) # will store what optimal IR gives result for the view IR.
        self.op_cmds = [] # this keeps store of all the different views of select so that, they will be showed as different fetches
        self.cmd_line_no = {}
        self.rm_cmds = []
    
    def IR_generation(self):
        for block in self.flat_code:
            if block['type'] == "select":
                if 'where' in block and 'orderBy' not in block:
                    self.IR.append(["select", block['select'], block['table_name'], block['where'], ""])
                elif 'orderBy' in block and 'where' not in block:
                    self.IR.append(["select", block['select'], block['table_name'], "", block['orderBy']])
                elif 'orderBy' not in block and 'where' not in block:
                    self.IR.append(["select", block['select'], block['table_name'], "", ""])
                else:
                    self.IR.append(["select", block['select'], block['table_name'], block['where'], block['orderBy']])
                if 'view' in block:
                    self.IR.append(['view', block['view'], block['table_name']]) # add command to make view of the select that ends before it.

            elif block['type'] == "update":
                if 'where' in block:
                    self.IR.append(["update", block['set'], block['table_name'], block['where']])
                else:
                    self.IR.append(["update", block['set'], block['table_name'], ''])

            elif block['type'] == "delete":
                if 'where' in block:
                    self.IR.append(["delete", block['where'], block['table_name']])
                else:
                    self.IR.append(["delete", "", block['table_name']])

            elif block['type'] == "index":
                self.IR.append(['index', block['select'], block['table_name'], block['index_name']])

            elif block['type'] == 'hset':
                self.IR.append(['hset', block['key'], block['value']])
            elif block['type'] == 'hget':
                self.IR.append(['hget', block['key']])

            elif block['type'] == "flat_block":
                for inst in block["flat_expr"]:
                    flat_ast = ast.parse(inst)
                    # print(ast.dump(flat_ast, indent=2))
                    if isinstance(flat_ast, Module):
                        for st in flat_ast.body:
                            if isinstance(st, Assign):
                                tar = st.targets[0].id
                                val = st.value
                                if isinstance(val, Compare):                                                                        
                                    comp_val = val.comparators[0].id if isinstance(val.comparators[0], Name) else val.comparators[0].value                                    

                                    if isinstance(val.ops[0], Eq):
                                        self.IR.append(["equals", val.left.id, comp_val, tar])
                                    elif isinstance(val.ops[0], NotEq):
                                        self.IR.append(["nequals", val.left.id, comp_val, tar])
                                    elif isinstance(val.ops[0], Lt):
                                        self.IR.append(["lt", val.left.id, comp_val, tar])
                                    elif isinstance(val.ops[0], LtE):
                                        self.IR.append(["lte", val.left.id, comp_val, tar])
                                    elif isinstance(val.ops[0], Gt):
                                        self.IR.append(["gt", val.left.id, comp_val, tar])
                                    elif isinstance(val.ops[0], GtE):
                                        self.IR.append(["gte", val.left.id, comp_val, tar])
                                elif isinstance(val, BoolOp):
                                    if isinstance(val.op, And):
                                        self.IR.append(["and", val.values[0].id, val.values[1].id, tar])
                                    elif isinstance(val.op, Or):
                                        self.IR.append(["or", val.values[0].id, val.values[1].id, tar])
                                elif isinstance(val, UnaryOp):
                                    if isinstance(val.op, Not):
                                        self.IR.append(["not", val.operand.id, tar])
            elif block['type'] == "import_table":
                self.IR.append(['create_table', block['table_name'], block['url']])
        return

    def _check_if_update(self, i, j, table_name):
        for k in range(i, j):
            inst = self.IR[k]
            if inst[0] in ["update", "delete"] and inst[2] == table_name:
                return True
            elif inst[0] == "create_table" and inst[1] == table_name:
                return True
        return False
    
    def _check_if_view(self, i, j, table_name): #actually only need to check if you wanna make a view of i or j. if yes then avoid it.
        if i+1 < len(self.IR):
            inst = self.IR[i+1]
            if inst[0] == "view" and inst[2] == table_name:
                return True
        if j+1 < len(self.IR):
            inst = self.IR[j+1]
            if inst[0] == "view" and inst[2] == table_name:
                return True
        return False

    def _rm_inst(self, inst_rm):
        for i in reversed(inst_rm): # to preserve indexes of the inst to remove
            self.rm_cmds.append(self.IR[i])
            self.IR.pop(i)

    def optimize_batch_processing(self):    

        # delete all ops after a full table delete
        tbl_del_id = {}
        inst_rm = []
        #print("APPLYING DELETE OPTIM")
        for idx, inst in enumerate(self.IR):
            if inst[0] == "delete" and inst[1] == "":
                tbl_del_id[inst[2]] = idx
            print(inst)
            if inst[0] in ["select", 'update', 'delete', 'index', 'view'] and inst[2] in tbl_del_id and tbl_del_id[inst[2]] < idx:
                inst_rm.append(idx)
            if inst[0] == "create_table" and inst[1] in tbl_del_id:
                del tbl_del_id[inst[1]]
        
        self._rm_inst(inst_rm)

        inst_rm = []
        # merging selects
        self.IR_view = deepcopy(self.IR)
        for i in range(len(self.IR)):
            for j in range(i+1, len(self.IR)):
                inst_i = self.IR[i]
                inst_j = self.IR[j]

                if i != j and (inst_i[0] == 'select' and inst_j[0] == 'select') and (inst_i[2] == inst_j[2]): # different select statements on same table
                    #print("FOUND 2 SELECTS ON SAME TABLE \n\n")
                    # check if there is an view to this table in between: if yes then stop this optimization, else
                    if self._check_if_view(i, j, inst_i[2]) or self._check_if_update(i, j, inst_i[2]):
                        break
                    else:
                        #print(f"2 SELECTS DONT HAVE UPDATE ON SAME TABLE: {i}, {j} \n\n")

                        cond_i = self.IR[i][3]
                        cond_j = self.IR[j][3]

                        cols_i = set(self.IR[i][1])
                        cols_j = set(self.IR[j][1])
                        # check if they have no where condition or same where condition, or only one has where condition.
                        if (cond_i == cond_j) or cond_j == '' or cond_i == '':
                            if cond_i == '':
                                cond = cond_i
                            elif cond_j == '':
                                cond = cond_j
                            elif cond_i == cond_j:
                                cond = cond_i
                            #print("MERGED COND", cond)
                            # merge cols                            
                            if ('*' in cols_j or '*' in cols_i) or (cols_i.issubset(cols_j) or cols_j.issubset(cols_i)):
                                if cols_i.issubset(cols_j) or '*' in cols_j:
                                    col = cols_j
                                elif cols_j.issubset(cols_i) or '*' in cols_i:
                                    col = cols_i
                                elif cols_i == cols_j:
                                    col = cols_i
                                #print("MERGED SUBSET", col)
                                
                                # make new select inst at both values, remove duplicates later.
                                new_select = ['select', col, inst_i[2], cond, ""]
                                self.IR[i] = new_select
                                #print(i, j, new_select)
                                self.view_to_IR[i].append(j)
                                inst_rm.append(j)
                            else:
                                break
                        else:
                            break

                    # check if there is an update to this table in between: if yes then stop this optimization, else
        self._rm_inst(inst_rm)
        inst_rm = []
        # if 2 indexes created on same table without update remove the latest one.
        for i in range(len(self.IR)):
            for j in range(i+1, len(self.IR)):
                i_inst, j_inst = self.IR[i], self.IR[j]
                if i_inst[0] == "index" and i_inst[0] == j_inst[0]:
                    # both are index queries, now check if same table and same cols.
                    if i_inst[1] == j_inst[1] and i_inst[2] == j_inst[2]:
                        #all are same, just named differently.
                        if self._check_if_update(i, j, i_inst[2]): # if true there is an update between 2 indexes so do nothing else remove latest one
                            break
                        else:
                            inst_rm.append(j)
        self._rm_inst(inst_rm)
        inst_rm = []

        return self.view_to_IR
        # CAN'T REMOVE DUPLICATES BLINDLY, NEED TO REMOVE THE INSTRUCTIONS FROM IR THAT ARE USELESS.
        # can create 2 views that are same with different name, if same name it will overwrite.

    def calc_cost(self):
        cost = []
        for inst in self.rm_cmds:
            if inst[0] == "select":
                cost.append([inst, 1, "Full Table Scan"])
            elif inst[0] == "delete":
                cost.append([inst, 1, "Metadata Lookup"])
            elif inst[0] == "index":
                cost.append([inst, 1, "Full Table Scan", 1, "Index Building"])
        return cost
    
    def _remove_duplicate_conditions(self):
        inst_rm = []
        for k, v in self.duplicates.items():
            if len(v) > 1: #then only select the assignment of the first one and then sub all places with this condition.
                init_def = v[0]
                to_exchange = v[1:]
                for idx, inst in enumerate(self.IR):
                    for dup in to_exchange:
                        if dup in inst:
                            # duplicte used here: can be assigned or used if assigned remove this inst else replace with init_def
                            if inst[0] in ['gt', 'gte', 'lt', 'lte', 'and', 'or', 'equals', 'nequals'] and dup == inst[3]: #assignment
                                inst_rm.append(idx)
                            elif inst[0] =='hset' and dup == inst[1]:
                                inst_rm.append(idx)
                            else: #sub with the init_def
                                sub_idx = inst.index(dup)
                                inst[sub_idx] = init_def
        self._rm_inst(inst_rm)
         
    def _lvn(self):
        # always gets the basic blocks
        current_value = -1
        value_numbers = dict()
        self.duplicates = defaultdict(list)
        
        def get_curr_val():
            nonlocal current_value
            current_value += 1
            return current_value

        get_val = lambda x: get_curr_val() if x not in value_numbers else value_numbers[x]
        
        get_old_eq_val = lambda x,y : value_numbers[f"{x}=={y}"] if f"{x}=={y}" in value_numbers else get_curr_val()
        get_old_neq_val = lambda x,y : value_numbers[f"{x}!={y}"] if f"{x}!={y}" in value_numbers else get_curr_val()
        get_old_lt_val = lambda x,y : value_numbers[f"{x}<{y}"] if f"{x}<{y}" in value_numbers else get_curr_val()
        get_old_lte_val = lambda x,y : value_numbers[f"{x}<={y}"] if f"{x}<={y}" in value_numbers else get_curr_val()
        get_old_gt_val = lambda x,y : value_numbers[f"{x}>{y}"] if f"{x}>{y}" in value_numbers else get_curr_val()
        get_old_gte_val = lambda x,y : value_numbers[f"{x}>={y}"] if f"{x}>={y}" in value_numbers else get_curr_val()

        get_old_and_val = lambda x,y : value_numbers[f"{x}and{y}"] if f"{x}and{y}" in value_numbers else get_curr_val()
        get_old_or_val = lambda x,y : value_numbers[f"{x}or{y}"] if f"{x}or{y}" in value_numbers else get_curr_val()



        #this will only work for compile time vars need to allocate value to runtime vars also
        
        for idx in range(len(self.IR)):
            # print("\n\n")
            # print(value_numbers)
            inst = self.IR[idx]
            # print(idx, inst)
            
            if inst[0] == 'hset':
                value_numbers[inst[2]] = get_val(inst[2])
                value_numbers[inst[1]] = value_numbers[inst[2]]

            if inst[0] == "equals":

                value_numbers[inst[1]] = get_val(inst[1])
                value_numbers[inst[2]] = get_val(inst[2])
                value_numbers[inst[3]] = get_old_eq_val(value_numbers[inst[1]], value_numbers[inst[2]])
                x = value_numbers[inst[1]]
                y = value_numbers[inst[2]]
                value_numbers[f"{x}=={y}"] = value_numbers[inst[3]]

            if inst[0] == "nequals":
                value_numbers[inst[1]] = get_val(inst[1]) # if the first operand is an int, assign it a value else we know that it will be live
                value_numbers[inst[2]] = get_val(inst[2])
                value_numbers[inst[3]] = get_old_neq_val(value_numbers[inst[1]], value_numbers[inst[2]])
                x = value_numbers[inst[1]]
                y = value_numbers[inst[2]]
                value_numbers[f"{x}!={y}"] = value_numbers[inst[3]]

            
            if inst[0] == "lte":
                value_numbers[inst[1]] = get_val(inst[1]) # if the first operand is an int, assign it a value else we know that it will be live
                value_numbers[inst[2]] = get_val(inst[2])
                value_numbers[inst[3]] = get_old_lte_val(value_numbers[inst[1]], value_numbers[inst[2]])
                x = value_numbers[inst[1]]
                y = value_numbers[inst[2]]
                value_numbers[f"{x}<={y}"] = value_numbers[inst[3]]

            
            if inst[0] == "lt":
                value_numbers[inst[1]] = get_val(inst[1]) # if the first operand is an int, assign it a value else we know that it will be live
                value_numbers[inst[2]] = get_val(inst[2])
                value_numbers[inst[3]] = get_old_lt_val(value_numbers[inst[1]], value_numbers[inst[2]])
                x = value_numbers[inst[1]]
                y = value_numbers[inst[2]]
                value_numbers[f"{x}<{y}"] = value_numbers[inst[3]]

            
            if inst[0] == "gte":
                value_numbers[inst[1]] = get_val(inst[1]) # if the first operand is an int, assign it a value else we know that it will be live
                value_numbers[inst[2]] = get_val(inst[2])
                value_numbers[inst[3]] = get_old_gte_val(value_numbers[inst[1]], value_numbers[inst[2]])
                x = value_numbers[inst[1]]
                y = value_numbers[inst[2]]
                value_numbers[f"{x}>={y}"] = value_numbers[inst[3]]

            
            if inst[0] == "gt":
                value_numbers[inst[1]] = get_val(inst[1]) # if the first operand is an int, assign it a value else we know that it will be live
                value_numbers[inst[2]] = get_val(inst[2])
                value_numbers[inst[3]] = get_old_gt_val(value_numbers[inst[1]], value_numbers[inst[2]])
                x = value_numbers[inst[1]]
                y = value_numbers[inst[2]]
                value_numbers[f"{x}>{y}"] = value_numbers[inst[3]]

            
            if inst[0] == "and":
                value_numbers[inst[1]] = get_val(inst[1]) # if the first operand is an int, assign it a value else we know that it will be live
                value_numbers[inst[2]] = get_val(inst[2])
                value_numbers[inst[3]] = get_old_and_val(value_numbers[inst[1]], value_numbers[inst[2]])
                x = value_numbers[inst[1]]
                y = value_numbers[inst[2]]
                value_numbers[f"{x}and{y}"] = value_numbers[inst[3]]

            
            if inst[0] == "or":
                value_numbers[inst[1]] = get_val(inst[1]) # if the first operand is an int, assign it a value else we know that it will be live
                value_numbers[inst[2]] = get_val(inst[2])
                value_numbers[inst[3]] = get_old_or_val(value_numbers[inst[1]], value_numbers[inst[2]])
                x = value_numbers[inst[1]]
                y = value_numbers[inst[2]]
                value_numbers[f"{x}or{y}"] = value_numbers[inst[3]]
            if inst[0] in ['equals', 'nequals', 'or', 'and', 'gt', 'gte', 'lt', 'lte']:
                self.duplicates[value_numbers[inst[3]]].append(inst[3])
            if inst[0] == 'hset':
                self.duplicates[value_numbers[inst[2]]].append(inst[1])
            # print("VALUE_NUMBERS", value_numbers)
            # print("DUPLICATES", self.duplicates)
            # print("SUBBED INST", self.IR[idx])]
        self._remove_duplicate_conditions()
    
if __name__ == "__main__":
    flat_code1 = [{'type': 'flat_block', 'flat_expr': ['condition1 = last_name == Smith', 'condition2 = first_name != Alfred', 'condition3 = condition1 and condition2', 'condition4 = first_name != Alfred']},
    #{'select': ['*'], 'table_name': 'CUSTOMERS', 'orderBy': ('col1', 'DESC'), 'type': 'select'},
    {'select': ['col1', 'col2'], 'table_name': 'CUSTOMERS', 'type': 'select'},
    {'select': ['col1', 'col2'], 'table_name': 'CUSTOMERS', 'where': 'condition3', 'type': 'select'},
    {'set': 'condition3', 'table_name': 'CUSTOMERS', 'type': 'update'},
    {'table_name': 'CUSTOMERS', 'type': 'delete'},
    {'select': ['col1', 'col2'], 'table_name': 'CUSTOMERS', 'where': 'condition3', 'type': 'select'}, # should be gone
    {'type': 'flat_block', 'flat_expr': ['del_cond = first_name != Alfred']},
    {'table_name': 'CUSTOMERS', 'where': 'del_cond', 'type': 'delete'}, # should be gone
    {'select': ['*'], 'index_name': 'short_customer', 'table_name': 'CUSTOMERS', 'type':'index'}, # should be gone
    {'url': 'http://example.com', 'table_name': 'CUSTOMERS', 'header': 'False', 'type': 'import_table'},
    {'select': ['col1', 'col2'], 'table_name': 'CUSTOMERS', 'where': 'condition3', 'type': 'select'}, # should be gone
    {'select': ['*'], 'index_name': 'short_customer', 'table_name': 'CUSTOMERS', 'type':'index'}]

    flat_code2 = [{'type': 'flat_block', 'flat_expr': ['condition1 = last_name == Smith', 'condition2 = first_name != Alfred', 'condition3 = age > 18', 'condition4 = condition1 and condition2', 'condition5 = condition4 or condition3']},
    {'select': ['*'], 'table_name': 'CUSTOMERS', 'orderBy': ('col1', 'DESC'), 'type': 'select'},
    {'select': ['col1', 'col2'], 'table_name': 'CUSTOMERS', 'type': 'select'},
    {'select': ['col1', 'col2'], 'table_name': 'CUSTOMERS', 'where': 'condition4', 'type': 'select'},
    {'set': ('age', 18), 'table_name': 'CUSTOMERS', 'type': 'update'},
    {'table_name': 'CUSTOMERS', 'type': 'delete'},
    {'type':'hset', 'key': 'a', 'value': 1},
    {'type':'hset', 'key': 'b', 'value': 1},
    {'type':'hget', 'key': 'a', },
    {'type':'hget', 'key': 'b', },

    {'select': ['col1', 'col2'], 'table_name': 'CUSTOMERS', 'where': 'condition5', 'type': 'select'}, # should be gone
    {'type': 'flat_block', 'flat_expr': ['del_cond = first_name != Alfred']},
    {'table_name': 'CUSTOMERS', 'where': 'del_cond', 'type': 'delete'}, # should be gone
    {'select': ['*'], 'index_name': 'short_customer', 'table_name': 'CUSTOMERS', 'type':'index'}, # should be gone
    {'url': 'http://example.com', 'table_name': 'CUSTOMERS', 'header': 'False', 'type': 'import_table'},
    {'select': ['col1', 'col2'], 'table_name': 'CUSTOMERS', 'where': 'condition3', 'type': 'select'}, # should be gone
    {'select': ['*'], 'index_name': 'short_customer', 'table_name': 'CUSTOMERS', 'type':'index'}]

    flat_code = flat_code2  
    assm = Assembler(flat_code)
    assm.IR_generation()
    for i, inst in enumerate(assm.IR):
        print(i, inst)

    print("\n")
    assm._lvn()
    print("\n\nAFTER LVN OPTIMIZATION")
    for i, inst in enumerate(assm.IR):
        print(i, inst)
    
    print(assm.duplicates)


    view_to_IR = assm.optimize_batch_processing()
    print("\n\nAFTER BATCH OPTIMIZATION")
    for k, vs in view_to_IR.items():
        for v in vs:
            print(assm.IR[k], "services", assm.IR_view[v])

    print("\n\n")
    for i, inst in enumerate(assm.IR):
        print(i, inst)

    print("\n\nMinimum Performance Improvements by Optimization (Higher Gains when data is larger, as more disk calls will be avoided):")
    cost = assm.calc_cost()
    for item in cost:
        print(*item)
