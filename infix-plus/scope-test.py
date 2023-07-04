def inner(ls : list):
    return ls[0:2]

def outer(ls : list):
    my_list = ls
    inside = inner(my_list)
    my_list = my_list[-2:]
    return inside

print(outer([[1],[2],[3],[4],[5]]))