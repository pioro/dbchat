# simple data type
number = 1
print number

str = "This is string"
print str

# tuple 
no_tuple = (1,2)

print no_tuple

str_tuple = ('This is col1', 'This is col2')

print str_tuple
print str_tuple[0]
print str_tuple[1]

# list 

first_list = [ 1, 2, 3, 4]
print first_list

for i in first_list:
    print i


sec_list = [ x*x for x in first_list ] 
print sec_list


tuple_list = [ (1, 'String1'), (1, 'String1'), (2, 'String2'), (3, 'String3') ]
print tuple_list

small_list = [ x for x in tuple_list if x[0] == 2 ]
print small_list

