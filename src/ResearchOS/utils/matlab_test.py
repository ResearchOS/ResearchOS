import time
import matlab.engine

import numpy as np

eng = matlab.engine.connect_matlab(name = "test")

# Construct a variable similar to my actual one.
N = 43960 # x 3 columns = 1MB matlab.double
dummy_struct = {}
for i in range(1, 101):
    field_name = f'field{i}'
    # Create an Nx3 matrix of matlab doubles
    # matrix = eng.randn(N, 3, nargout=1)
    matrix = [[float('nan'), float('nan'), float('nan')] for i in range(N)]
    dummy_struct[field_name] = matrix

var_i8_30M = matlab.int8([1 for i in range(30000000)])
var_d_30M = matlab.double([1 for i in range(30000000)])

const_1200M = 1200000000
var_i8_1200M = matlab.int8(vector=[1 for i in range(const_1200M)],size=(1,const_1200M))



before = time.perf_counter()
eng.workspace['var_i8_30M'] = var_i8_30M
after = time.perf_counter()
elapsed_i8 = after - before
print("int8: ", elapsed_i8)

before = time.perf_counter()
eng.workspace['var_d_30M'] = var_d_30M
after = time.perf_counter()
elapsed_d = after - before
print("double: ", elapsed_d)

before = time.perf_counter()
eng.workspace['dummy_struct'] = dummy_struct
after = time.perf_counter()
elapsed_struct = after - before
print("struct: ", elapsed_struct)