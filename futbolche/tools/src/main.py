from chatbot import parse_input as parse_input_nlu

if __name__ == '__main__':
    print('Tools main - lightweight runner')
    intent, params = parse_input_nlu('помощ')
    print(intent, params)
