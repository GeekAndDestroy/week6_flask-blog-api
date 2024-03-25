

def decorator(func):
    def inner():
        print('Something is happening before the function')
        func()
        print('Something is happening after the function')
    return inner

@decorator
def jump():
    print('I am jumping')

@decorator
def swim():
    print('I am swimming')


# jump = decorator(jump)
jump()

# swim = decorator(swim)
swim()