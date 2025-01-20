import numpy as np

integers = [1, 3, 0, 2, 4]

array = np.array(integers)

indices = np.arange(len(array))
total_weighted_index = np.sum(indices * array)

total_count = np.sum(array)

average_index = total_weighted_index / total_count if total_count > 0 else 0

