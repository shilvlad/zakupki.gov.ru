import time

def time_of_function(function):
    def wrapped(*args):
        start_time = time.clock()
        res = function(*args)
        print("Время выполнения:",time.clock() - start_time)
        return res
    return wrapped