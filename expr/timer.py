import time

def timer(func):
    def timed_func(*args):
        start = time.time()
        rst = func(*args)
        end = time.time()
        cost = time.strftime("%H:%M:%S", time.gmtime(end - start))
        print(f"{func.__name__} function cost time: {cost} ", end="")
        return rst

    return timed_func