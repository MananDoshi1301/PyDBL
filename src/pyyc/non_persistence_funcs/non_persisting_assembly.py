

class NonPersistingAssembly():

    def __init__(self):
        self.assembly = []
        ...

    def __del__(self):
        # print("\n".join(self.assembly))
        ...

    def add_assembly(self, lst):
        self.assembly.append(lst)        

    def add_query(self, query):

        query_type = query[0]
        if query_type == 'hset':
            register, value = query[1:]
            value = '$' + str(value)
            register = '%' + register
            lst = ['movl', value + ',', register]
            lst = " ".join(lst)
            self.add_assembly(lst)            
