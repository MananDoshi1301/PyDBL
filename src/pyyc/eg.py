# select('*', table="CUSTOMERS", where="last_name = 'smith'")
# condition = (not {"last_name": "smith"} and not {"first_name": "Jones"}) or {}
# condition = {">": (height, 7)}
# condition = {"==": (last_name, "smith")} and {"!=": (first_name, "jones")}