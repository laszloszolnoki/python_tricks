import inspect
from types import SimpleNamespace
from functools import wraps

def namespaced(dict_mode=False, return_args: list = None, result_var='result'):
    """
    Author: Szolnoki, László
    version: 1.0
    Issue date: 2024-FEB-24
    Using this decorator the return value of the decorated function will be a simple namespace. Which will contain
    the result under the key 'result' (configurable name) and will also contain all args and kwargs (can be selected which to include).

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
