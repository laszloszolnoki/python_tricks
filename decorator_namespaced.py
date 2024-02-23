import inspect
from types import SimpleNamespace
from functools import wraps

def namespaced(func):
    """
    Using this decorator the return value of the function will be a simple namespace. Which will contain
    the result under the key 'result' and will also contain all args and kwargs.
    
    Example usage:
    @namespaced
    def testfunc(arg1, arg2, kwarg1='', kwarg2=''):
        some_inner_var = "ff"
        return arg1 + arg2
    
    testres = testfunc(1,2, kwarg1="a", kwarg2="b")
    print(testres)
    #Output: namespace(result=3, arg1=1, arg2=2, kwarg1='a', kwarg2='b')
    print(testres.result, testres.arg1, testres.arg2, testres.kwarg1, testres.kwarg2)
    #Output: 3 1 2 a b
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Call the original function
        result = func(*args, **kwargs)
        # Create a SimpleNamespace with the result, arguments, and keyword arguments
        all_args = {arg: value for arg, value in zip(inspect.getfullargspec(func).args, args)}
        all_args.update(kwargs)
        return SimpleNamespace(result=result, **all_args)
    return wrapper
