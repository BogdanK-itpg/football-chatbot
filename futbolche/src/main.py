from chatbot.chatbot import parse_input as parse_input_nlu, handle_intent as handle_intent_router
from db import initialize_database
from utils.logger import log_command


# Initialize database immediately on program start
initialize_database()


def main():
    print("Football League Chatbot")
    print("Напишете 'помощ' за команди.")

    while True:
        user_input = input(">> ")

        intent, params = parse_input_nlu(user_input)
        response = handle_intent_router(intent, params)

        if response == "exit":
            print("До скоро!")
            break

        print(response)
        log_command(user_input, response)


if __name__ == "__main__":
    main()
