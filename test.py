def change_token():
    global current_token
    token_index = tokens.index(current_token)
    if token_index >= len(tokens) - 1:
        current_token = tokens[0]
    else:
        current_token = tokens[token_index + 1]


if __name__ == '__main__':
    tokens = ["1", "2", "3", "4"]
    current_token = tokens[0]
    while True:
        print(current_token)
        change_token()
