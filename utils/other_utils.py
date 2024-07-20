# converting string to int if possible, otherwise keeping it as string
def convert_to_int_or_keep_as_string(input_string):
    try:
        return int(input_string)
    except ValueError:
        return input_string
