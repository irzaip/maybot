from backend.conversations import Conversation, Message, Persona
from backend import ollama_api as api

async def run(self, conv_obj: Conversation, message: Message) -> str:
    """Run friend conversation handler"""
    msg_text = message.text
    
    #buat vold, gak perlu memory
    if conv_obj.persona == Persona.VOLD:
        memory = False
    else:
        memory = True

    result = await api.ask_gpt(self, conv_obj, msg_text, memory=memory)
    return result
