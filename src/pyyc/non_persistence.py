

class NonPersistence():

    def __init__(self, query_order, non_persisting_assembly_channel):
        self.register_map = {"eax": "", "ebx": "", "ecx": "", "edx": "", "esi": "", "edi": ""}
        self.query_order = query_order
        self.vector_clock = 0
        self.least_value = ()
        # All keys other than also those not in registers (key: value)
        self.active_keys = {}
        self.assembly = []
        
        # key: (register, vector_clock)
        self.lru = {}
        self.available_registers = ["eax", "ebx", "ecx", "edx", "esi", "edi"]
        self.non_persisting_assembly_object = non_persisting_assembly_channel

    def __del__(self):
        # print(self.assembly)
        ...

    def find_least_used(self):
        min_val = self.vector_clock
        min_key = ""
        for k, v in self.lru.items():
            if v[1] < min_val:
                min_val = v[1]
                min_key = k

        return min_key

    def append_assembly(self, operation, location, value = 0):
        
        lst = [operation, location]
        if operation == 'hset':
            lst.append(value)
                
        self.non_persisting_assembly_object.add_query(lst)

    def set_key(self, key, value):
        
        # Updating key if already present in lru or register
        if key in self.lru:
            register = self.lru[key][0]
            # Update vector time for existing key
            self.lru[key] = (register, self.vector_clock)
            # Update value for existing key
            self.active_keys[key] = value
            # Set new value to assembly too
            self.append_assembly('hset', register, value)
            print(key, '=', value)
            self.vector_clock += 1

            
        else:
            # if lru empty?: push to that register
            if self.available_registers:     
                register = self.available_registers.pop(0)               
                self.lru[key] = (register, self.vector_clock)
                self.register_map[register] = key

                # Moving to stack
                self.active_keys[key] = value
                
                # Set new value to assembly too                
                self.append_assembly('hset', register, value)
                print(key, '=', value)
                self.vector_clock += 1
                
            # else: substitute with least recently used value             
            else:

                # Get key who is in a register and is not used for a long time
                min_key = self.find_least_used()
                self.available_registers.append(self.lru[min_key][0])            
                self.lru.pop(min_key)
                self.set_key(key, value)

        print("##LRU: ", self.lru, '\n')
        # print("##Register_map: ", self.register_map)
        # print("##Active Keys", self.active_keys, "\n")        

    def get_key(self, key):
        # If key is present in lru:
            # Check if present in 
        if key in self.active_keys:
            if key in self.lru:
                # Extract using register
                register = self.lru[key][0]
                # Update vector time for existing key
                self.lru[key] = (register, self.vector_clock)
                
                # Reading value from assembly                
                self.vector_clock += 1
                
            else:
                # Return from variable
                value = self.active_keys[key]
                self.set_key(key, value)
            
            print(key, ":", self.active_keys[key])        
            print("##LRU: ", self.lru, '\n')

    def process_queries(self):  

        for query in self.query_order:

            query_type = query[0]
            
            if query_type == 'hset':
                key, value = query[1:]
                self.set_key(key, value)

            elif query_type == 'hget':
                key = query[1]
                self.get_key(key)




if __name__ == "__main__":

    query = [
        ['hset', 'a', 1],
        ['hset', 'b', 2],
        ['hset', 'c', 3],
        ['hset', 'd', 4],
        ['hset', 'e', 5],
        ['hset', 'f', 6],
        ['hset', 'g', 7],
    ]

    # query = [

    # ]


    np = NonPersistence(query)
    np.process_queries()
