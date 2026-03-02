import sys
import os
import importlib.util
# Load the top-level chatbot module file (avoid package name collision)
chatbot_path = os.path.join(os.getcwd(), 'src', 'chatbot.py')
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
spec = importlib.util.spec_from_file_location('chatbot_module', chatbot_path)
chatbot_mod = importlib.util.module_from_spec(spec)
sys.modules['chatbot_module'] = chatbot_mod
spec.loader.exec_module(chatbot_mod)
parse_input = chatbot_mod.parse_input
get_random_response = chatbot_mod.get_random_response

samples = [
    'браво',
    'много добре',
    'добра работа',
    'страхотно',
    'добави играч Петър Бербатов в клуб Левски позиция FW номер 9 националност България дата на раждане 1981-02-01 статус Активен'
]

for s in samples:
    intent, params = parse_input(s)
    print(s, '=>', intent, params)
    if intent == 'praise':
        print('sample response:', get_random_response(intent))
