from functools import reduce

def pipe(*functions):
    """Allows 'chaining' (or 'piping') functions together à la Elixir or Clojure.
    Example usage:
    def add1(x, message=None):
        if message :
            print('Message: ', message)
        return 1 + x

    result = pipe(
        1,
        add1,
        lambda x: add1(x, message='Hello'),
        add1,
    )
    #Output: Hello
    print(result)
    #Output: 4
    """
    return reduce(
        lambda x, f: f(x) if not isinstance(x, list) else f(*x),
        functions,
    )
    

def chain_functions(*functions):
    """
    Chaining functions together using the pipe() function
    Example usage:
    def add1(x, message=None):
    if message :
        print('Message: ', message)
    return 1 + x
    add3 = chain_functions(add1, partial(add1, message='Hello'), add1)
    print(add3(1))
    # Output: Message:  Hello; 4
    """
    return lambda x: pipe(x, *functions)
