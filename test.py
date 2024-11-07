def task_1():
    students = {"Tom", "Bob", "Sam"}
    employees = {"Tom", "Bob", "Alex", "Mike"}
    print("Люди в обоих группах", employees | students)
    print("Люди которые одновременно учатся и работают",  employees & students)
    print("Люди которые только учатся", students - employees)
    print("Люди которые или учатся, или работабют, но не одновременно", students ^ employees)

def task_2():
    input_data ="""69485 Jack 
        95715 qwerty 
        95715 Alex 
        83647 M
        197128 qwerty 
        95715 Jack 
        93289 Alex 
        95715 Alex 
        95715 M
    """
    input_data.strip()
    input_data.split()