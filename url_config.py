try:
    with open('urls.txt', 'r') as file:
        urls = [ line.rstrip() for line in file.readlines()]
except FileNotFoundError:
    raise Exception('urls.txt not found.')