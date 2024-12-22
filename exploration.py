import matplotlib.pyplot as plt
from indexing import SqliteInvertedIndex

print("hi")


inverted_index = SqliteInvertedIndex("inverted_index.db")
inverted_index_matrix = inverted_index.get_matrix()
print(inverted_index_matrix.size)

# |%%--%%| <JJTU8YYM7y|O3AiHggqL4>
