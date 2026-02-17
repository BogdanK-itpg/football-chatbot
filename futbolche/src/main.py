import chatbot
from datetime import datetime

LOG_FILE = "../commands.log"

def log_command(user_input, result):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} | {user_input} | {result}\n")


def main():
    print("Football League Chatbot")
    print("Напишете 'помощ' за команди.")

    while True:
        user_input = input(">> ")

        intent, param = chatbot.parse_input(user_input)
        response = chatbot.handle_intent(intent, param)

        if response == "exit":
            print("До скоро!")
            break

        print(response)
        log_command(user_input, response)


if __name__ == "__main__":
    main()
