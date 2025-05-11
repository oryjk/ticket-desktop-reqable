import socket
import uuid

result = map(lambda x: x ** 2, [1, 2, 3, 4, 5])
for value in result:
    print(value)
print(list(result))


my_dict_1=dict(name="wang",age=12)
print(my_dict_1)
my_dict_2=dict([('name','wang'),('age',12)])
print(my_dict_2)

def my_decorator(func):
    def wrapper():
        print("Something is happening before the function is called.")
        func()
        print("Something is happening after the function is called.")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()

identifiers = []
mac_addresses = uuid.getnode()
identifiers.append(':'.join(['{:02x}'.format((mac_addresses >> i) & 0xff) for i in range(0, 8 * 6, 8)][::-1]))
identifiers.append(socket.gethostname())
print(identifiers)