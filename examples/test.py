import os

print(__file__)
print(os.path.abspath(os.path.join(__file__, os.pardir)))
print(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)))
