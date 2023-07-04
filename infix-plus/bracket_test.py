def build_recursive(depth : int):
    if depth == 0:
        return []
    return ((depth, build_recursive(depth-1)), [i for i in range(depth)])

a = build_recursive(300)

print(a)