import numpy as np
from copy import deepcopy
integers = [1, 3, 0, 2, 4]

array = np.array(integers)

indices = np.arange(len(array))
total_weighted_index = np.sum(indices * array)

total_count = np.sum(array)

average_index = total_weighted_index / total_count if total_count > 0 else 0

class Num:
    def __init__(self):
        self.num= 10
        self.string = String()

class String:
    def __init__(self):
        self.string = 'Chad'


def hello(n):
    if n.num == 20: return 1
    else:
        n = deepcopy(n)
        n.num += 1
        n.string.string += str(n.num)
        return hello(n)

if __name__ == '__main__':
    mynum = Num()
    hello(mynum)
    print(mynum.num, mynum.string.string)
    print(np.str_('B') == 'B')