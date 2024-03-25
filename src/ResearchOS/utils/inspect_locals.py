import sys
import ctypes
import psutil

def get_ref_count(var):
    # Use ctypes to get the memory address of the variable
    address = id(var)
    
    # Use sys.getrefcount on the variable
    ref_count = sys.getrefcount(var) - 3

    size = sys.getsizeof(var)
    
    return address, ref_count, size

def inspect_locals(local_vars: dict, do_run: bool = True):
    # Define some variables in the local namespace

    if not do_run:
        return

    # Iterate through the local namespace and print the variable names, memory address, and reference count
    total_size = 0
    for var_name, var_value in local_vars.items():
        address, ref_count, size = get_ref_count(var_value)
        # print(f"{var_name}: Size={size}, Address={address}, Ref Count={ref_count}")
        total_size += size

    # print(f"Total size of local variables: {sys.getsizeof(local_vars)}")
    # print(f"Total size of global variables: {sys.getsizeof(globals())}")
    memory_usage = get_memory_usage()
    print(f"Memory usage: {memory_usage}")

def get_memory_usage():
    # Get the memory usage of the current process
    process = psutil.Process()
    memory_info = process.memory_info()
    num_bytes = memory_info.rss
    return format_bytes(num_bytes)

def format_bytes(num_bytes: int) -> str:
    bytes_str = str(num_bytes)
    abbrevs = ["B", "KB", "MB", "GB", "TB", "PB"]
    idx = len(bytes_str) // 3
    num_places_left_of_dec = len(bytes_str) % 3
    if num_places_left_of_dec == 0:
        idx -= 1
        num_places_left_of_dec = 3
    num_places_right_of_dec = 2
    return f"{bytes_str[:num_places_left_of_dec]}.{bytes_str[num_places_left_of_dec+1:num_places_right_of_dec+num_places_left_of_dec+1]} {abbrevs[idx]}"
