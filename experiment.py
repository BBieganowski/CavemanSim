from caveman import Caveman
from jungle import Jungle
import pandas as pd
import numpy as np

# Create a jungle with 10 cavemen and 100 food units
jungle = Jungle(10, 0.3)

pop_dfs = []

for i in range(100):
    jungle.advance_year()
    pop_df = jungle.get_population_dataframe()
    pop_dfs.append(pop_df)

print("Done!")