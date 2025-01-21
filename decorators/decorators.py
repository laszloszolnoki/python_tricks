import inspect
from types import SimpleNamespace
from functools import wraps
import os
import sys
import traceback
#from multiprocessing import Process, Queue

# added run_in_subprocess() on 2025-JAN-21

def namespaced(dict_mode=False, return_args: list = None, result_var='result'):
    """
    Author: sl044
    version: 1.0
    Issue date: 2024-FEB-24
    Using this decorator the return value of the decorated function will be a simple namespace. Which will contain
    the result under the key 'result' (configurable name) and will also contain all args and kwargs with their values (can be selected which to include).
    Parameters:
        dict_mode (boolean, default=False) Return either a SimpleNamespace (dot notation accessing) or dictionary (bracket notation accessing)
        return_args (list, default=None) Specify in a list which arguments will be included of the return value of the decorated function
        result_var (string, default='result') The name of the var that contains the original return value of the decorated function
    
    Example usage:
    @namespaced()
    def testfunc(arg1, arg2, kwarg1='', kwarg2=''):
        some_inner_var = "ff"
        return arg1 + arg2
    testres = testfunc(1,2, kwarg1="a", kwarg2="b")
    print(testres)
    #Output: namespace(result=3, arg1=1, arg2=2, kwarg1='a', kwarg2='b')
    print(testres.result, testres.arg1, testres.arg2, testres.kwarg1, testres.kwarg2)
    #Output: 3 1 2 a b
    """
    def decorator(func) :    
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Call the original function
            result = func(*args, **kwargs)
            # Create a dict with the result, arguments, and keyword arguments
            all_args = {arg: value for arg, value in zip(inspect.getfullargspec(func).args, args)}
            all_args.update(kwargs)
            # Filter the arguments based on return_args
            if return_args :
                all_args = {arg: value for arg, value in all_args.items() if arg in return_args}
            # Decide if the return value of the decorated function will be a dict or a SimpleNamespace
            if dict_mode:
                return_val = {**all_args, **{'result' : result} }
                # Rename the 'result' key to the result_var (if provided)
                if result_var != 'result':
                    return_val[result_var] = return_val.pop('result')
                return return_val
            return_val = SimpleNamespace(result=result, **all_args)
            # Rename the 'result' property to the result_var (if provided)
            if result_var != 'result':
                return_val.__dict__[result_var] = return_val.__dict__.pop('result')
            return return_val
        return wrapper
    return decorator

def debug(func):
    """Print the function signature and return value"""
    @wraps(func)
    def wrapper_debug(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        value = func(*args, **kwargs)
        print(f"{func.__name__}() returned {repr(value)}")
        return value
    return wrapper_debug

def threadify_simple(max_workers=4):  # @threadify() makes this obsolete
    """
    Usage:
    @threadify_simple(max_workers=5)       
    def test_func(arg, **kwargs):               # Only works with keyword arguments. There is a special, mandatory arg: 'iterable' (which must be an iterable)
        step = kwargs['iteration']              # The threads will be launched with the 'iterable' split into 'iterations'. Which will be passed back to the original function.
        sleepseconds = kwargs['sleepseconds']
        message = kwargs['message'] if 'message' in kwargs.keys() else None
        print(f'Going to sleep in iteration {step} for {sleepseconds} seconds. BTW arg is: {arg}')
        if message :
            print(message)
        time.sleep(sleepseconds)
    
    #Call the function:
    test_step = [1, 2, 'c', 4, 5, 'f', 7, 8, 'i', 10]
    test_func('test_arg', iterable=test_step, sleepseconds=3, message='Oyasumi nasai!')
    """
    import concurrent.futures
    def decorator(func) :
        @wraps(func)
        def wrapper(*args, **kwargs):
            iterable = kwargs.pop('iterable')
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = [executor.submit(func, *args, iteration=i, **kwargs) for i in iterable]
                concurrent.futures.wait(futures)
                query_results = [future.result() for future in futures]
            return query_results
        return wrapper
    return decorator

def threadify(max_workers=4):
    """
    Author: sl044
    version: 1.0
    Issue date: 2024-MAR-02
    
    Multi-threaded calling of functions that can operate independently on elements of iterables (Mandatory kwarg iterable=<iterable> when calling the function).
    If there are 2 iterables that need to be zipped together to make pairs that the ThreadPoolExecutor can work on, pass an argument zipper=<zipper iterable> when calling the function.
    
    Usage:
    WITH ZIPPER: (two iterables will be zipped together and passed to the threads to work on)
    The var that will receive the iterations (elements of 'iterable' and 'zipper' which are mandatory keyword arguments when calling the function)
    should be the first 2 positional arguments in the function definition.
    
    @threadify(max_workers=4)
    def test_func_with_zip(stage, sleep_seconds, arg, **kwargs):  # In this example, 'stage' and 'sleep_seconds' (the 'iterable' and the 'zipper') should be the first 2 args.
        print(f'Going to sleep in iteration {stage} for {sleep_seconds} seconds. BTW arg is {arg}')
        time.sleep(sleep_seconds)
    
    #Call the function:
    test_step = [1, 2,'c', 4, 5,'f', 7, 8, 'i', 10]
    test_sleepseconds = [5, 4, 2, 5, 7] # You probably want these 2 iterables have the same length, not like in this example!
    test_func_with_zip('test_arg', iterable=test_step, zipper=test_sleepseconds) #elements of iterable and zipper will be passed back by the decorator to the original function as the first 2 positional arguments!
    
    WITHOUT ZIPPER: The threads will work on the elements of the iterable. The next element will be passed to the original function upon each iteration. Other arguments don't change during the iterations.
    @threadify(max_workers=4)
    def test_func_without_zip(stage, sleep_seconds, arg, message=None):    #without a zipper, sleep_seconds will be a 'uniform' parameter. 
        print(f'Going to sleep in iteration {stage} for {sleep_seconds} seconds. BTW arg is: {arg}')
        if message :
            print(message)
        time.sleep(sleep_seconds)
    
    #Call the function:
    test_step = [1, 2,'c', 4, 5,'f', 7, 8, 'i', 10]
    test_func_without_zip(iterable=test_step, sleep_seconds=3, arg='test_arg', message='Oyasumi nasai!')
    
    """
    import concurrent.futures
    def decorator(func) :
        @wraps(func)
        def wrapper(*args, **kwargs):
            iterable = kwargs.pop('iterable')
            zipper = kwargs.pop('zipper') if 'zipper' in kwargs.keys() else None
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                if zipper :
                    zipped = list(zip(iterable, zipper))
                    futures = [executor.submit(func, i, z, *args, **kwargs) for i, z in zipped]
                else:
                    futures = [executor.submit(func, i, *args, **kwargs) for i in iterable]
                concurrent.futures.wait(futures)
                query_results = [future.result() for future in futures]
            return query_results
        return wrapper
    return decorator

def run_in_subprocess(timeout=60*60*10):
    """
    Author: sl044
    version: 1.0
    Issue date: 2025-JAN-21
    Decorator that runs the decorated function in a subprocess with a timeout.
    Returns ('OK'|'ERROR', {'log': [log], 'result': [result]})
    
    # Example usage:
    @run_in_subprocess(timeout=6)
    def example_function(x, y, z=0):
        import time
        if z == -1:
            raise Exception('You are a nincompooh')
        time.sleep(5)
        print("This is a print statement.")
        return x + y + z
    """
    import subprocess
    import pickle
    import inspect
    import tempfile
    import os
    import sys
    from functools import wraps
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get the function definition as a string, but remove the decorator line
            func_code = inspect.getsource(func)
            # Remove the decorator line if it exists
            func_lines = func_code.splitlines()
            if func_lines[0].strip().startswith('@'):
                func_code = '\n'.join(func_lines[1:])
            
            func_name = func.__name__

            # Serialize the arguments
            serialized_args = pickle.dumps((args, kwargs))

            # Create a temporary file to store the function code and execution script
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.py') as temp_file:
                temp_filename = temp_file.name
                temp_output_filename = f"{temp_filename}.out"
                temp_file.write(f"""
import pickle
import sys
import io
import os

# Add the current directory to the PYTHONPATH
current_dir = r'{os.getcwd()}'
sys.path.append(current_dir)

# Redirect stdout to capture print statements
stdout = io.StringIO()
sys.stdout = stdout

{func_code}
args, kwargs = pickle.loads({serialized_args})
output = {func_name}(*args, **kwargs)

# Write the captured stdout and the function output to a temporary file
with open(r'{temp_output_filename}', 'wb') as f:
    pickle.dump((stdout.getvalue(), output), f)
""")

            result = {'status': 'OK', 'output': None}

            try:
                # Run the function in a subprocess
                process = subprocess.Popen(
                    [sys.executable, temp_filename],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True,
                    env={**os.environ, 'PYTHONPATH': os.getcwd()}
                )

                try:
                    stdout, stderr = process.communicate(timeout=timeout)
                    if process.returncode != 0:
                        result['status'] = 'ERROR'
                        result['output'] = {'log': stderr, 'result': None}
                    else:
                        # Read the output from the temporary file
                        with open(temp_output_filename, 'rb') as f:
                            captured_stdout, function_output = pickle.load(f)
                        result['output'] = {'log': captured_stdout.strip(), 'result': function_output}
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                    result['status'] = 'ERROR'
                    result['output'] = {'log': 'timeout', 'result': None}
            except Exception as e:
                result['status'] = 'ERROR'
                result['output'] = {'log': str(e), 'result': None}
            finally:
                # Clean up the temporary files
                os.remove(temp_filename)
                if os.path.exists(temp_output_filename):
                    os.remove(temp_output_filename)

            return result['status'], result['output']
        return wrapper
    return decorator
