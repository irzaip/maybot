from backend.conversations import Conversation, ConvMode, Message, Persona
from backend import ollama_api as api
from backend.db_oper import insert_conv
from backend.functions import interview as iv
from backend.agents import agent1 as ag1

def is_group(phone_number: str) -> bool:
    if phone_number.endswith('@g.us'):
        return True
    else:
        return False
    
def real_sender_(message: Message):
    if is_group(message.user_number):
        return message.author
    else:
        return message.user_number
    

async def run(self, conv_obj: Conversation, message: Message):
    def remove_flood():
        if message.author in conv_obj.anti_flood:
            while message.author in conv_obj.anti_flood:
                conv_obj.anti_flood.remove(message.author) 
        if message.user_number in conv_obj.anti_flood:
            while message.user_number in conv_obj.anti_flood:
                conv_obj.anti_flood.remove(message.user_number) 

    msg_text = message.text

    real_sender = real_sender_(message)
    if real_sender in conv_obj.anti_flood:
        return "Tunggu yaa gaaess, lagi mencoba menjawab temanmu. sabar donk. budayakan antri."
    else:
        conv_obj.anti_flood.append(real_sender)

    if conv_obj.persona == Persona.VOLD:
        memory = False
    else:
        memory = True

    if conv_obj.convmode == ConvMode.INTERVIEW:
        remove_flood()
        return iv.get_answer(conv_obj, message)

    if msg_text.startswith('carikan'):
        result = ag1.ask_lc(msg_text)
        remove_flood()
        return result

    result = await api.ask_gpt(self, conv_obj, msg_text, memory=memory)
    remove_flood()
    return result
