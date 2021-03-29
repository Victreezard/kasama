from random import choice


# Accepts a tuple choices and picks at random
# Input can be a tuple of string to return just one, or the tuple can start with a number and
# pick as many as that number
def randomize(inputs):
    inputs = list(inputs)
    if inputs[0].isdigit():
        number_of_results = int(inputs[0])
        inputs = inputs[1:]

        if number_of_results > len(inputs):
            return 'Results cannot be more than the choices!'
        elif number_of_results == 0:
            return 'Results cannot be zero!'

        results = []
        for _ in range(number_of_results):
            pick = choice(inputs)
            results.append(pick)
            inputs.remove(pick)
        return ', '.join(results)

    else:
        return choice(inputs)


if __name__ == "__main__":
    print(randomize(('-1', 'hhelloo')))
