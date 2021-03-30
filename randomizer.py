from random import choice


# Accepts a list or tuple of string called Choices that picks at random to return as Results
# Usage:
#   1. Choices can be a series of string to return one Result
#   2. Choices start with a number (must be a string) and return Results based on that number
#   3. Choices can have a range of two numbers (must be strings) and return one Result from them
def randomize(choices):
    if type(choices) == tuple:
        choices = list(choices)
    elif type(choices) is not list:
        return 'Choices can only be a list or tuple'

    if len(choices) == 2:
        if choices[0].isdigit() and choices[1].isdigit():
            # Usage #3
            return choice(range(int(choices[0]), int(choices[1]) + 1))

    elif choices[0].isdigit():
        number_of_results = int(choices[0])
        choices = choices[1:]

        if number_of_results > len(choices):
            return 'Results cannot be more than the choices!'
        elif number_of_results == 0:
            return 'Results cannot be zero!'

        results = []
        for _ in range(number_of_results):
            pick = choice(choices)
            results.append(pick)
            choices.remove(pick)
        # Usage #2
        return ', '.join(results)

    else:
        # Usage #1
        return choice(choices)


if __name__ == "__main__":
    choices = ['one', 'two', 'three', 'four', 'five']
    num_range = ['3', '7']
    print(randomize(choices))
    print(randomize(['3'] + choices))
    print(randomize(num_range))
    print(randomize(['6'] + choices))
    print(randomize('abcde'))
