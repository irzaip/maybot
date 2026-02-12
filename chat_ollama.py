from ollama import chat
from ollama import ChatResponse


messages = [{'role': 'system', 'content': 'Kamu adalah assisten indonesia, dan menjawab dalam bahasa indonesia. kamu akan melayani dengan baik'},
            {'role': 'user', 'content': 'Bagaimana kamu bisa memecahkan masalah sehari-hari?'},
            ]
response: ChatResponse = chat(model='qwen2.5:14b', messages=messages)

print(response.message.content)