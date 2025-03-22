from conversations import Conversation, Message, Persona
from colorama import Fore, Style, Back
import persona_func as pf
import shlex
from agent1 import ask_lc
from agent3 import ask_pdf
from db_oper import insert_conv
import datetime
import toml
import ollama_api as api
import asyncio
import requests
import sd_agent as sd


cfg = toml.load('config.toml')

def eta(conv_obj: Conversation) -> str:
    return f"""Assalamualaikum semua.
Nama saya {conv_obj.bot_name}, saya disini membantu kakak-kakak dan abang-abang semua, untuk minta
bantuan saya, tulis nama saya di depan setiap permintaan kalian.

misalnya: *{conv_obj.bot_name} buatkan saya pidato kepresidenan untuk menerima G20 sebagai aliansi indonesia* 

hihi, tapi ya gak gitu juga ya.. kan situ bukan presiden. :))
permintaan harus spesifik dan jelas, supaya saya bisa lebih mudah mengerjakannya. Tapi jangan susah-susah juga yaaa... saya kan cuma robot yg kecil dan imut. :))
"""

def help() -> str:
    return f""".reset: reset to default
.who: check persona and mode
.set x y: set *y* to variable *x*
.get *x*: get the value of *x*
.msg x y: send msg y to var*x*
.list: display all variables keys
.send:
.join:
.intro: 
.others:
.eta: terangkanlah (perkenalan)
""" 

class AdminMemory():
    def __init__(self):
        self.admin_var = {}


admin_memory = AdminMemory()

def set_sys_var(var: str, rest):
    setvar = var
    value = ""
    for i in rest:
        value = f"{value} {i}"
    admin_memory.admin_var[str(setvar)] = value.strip()
    return f"Done setting {str(setvar)} !"


async def run(msg_proc, conv_obj: Conversation, msg_text: str):
    print(f"{Style.BRIGHT}{Fore.CYAN}ADMIN COMMAND: {msg_text}{Style.RESET_ALL}")
    if msg_text.lower().startswith('.reset'):
        pf.set_persona(Persona.ASSISTANT, conv_obj)
        return pf.set_personality("Maya", "ASSISTANT", "Hai, Aku Maya, aku akan berusaha membantumu", conv_obj)
    if msg_text.lower().startswith('.who'):
        persona = conv_obj.persona
        mode = conv_obj.convmode
        return f'saya sekarang adalah {conv_obj.bot_name} dengan persona:{persona}, mode:{mode}'
    if msg_text.lower().startswith('.?'):
        return help()
    if msg_text.lower().startswith('.eta'):
        return eta(conv_obj)
    if msg_text.lower().startswith('.st'):
        return f"""ft: {conv_obj.free_tries}
fg: {conv_obj.free_gpt}
fc: {conv_obj.funny_counter}
pm: {conv_obj.paid_messages}
prs: {conv_obj.persona}
cm : {conv_obj.convmode}
ct : {conv_obj.convtype}
        """

    command = msg_text.lower().split(" ")
    match command:
        case [".set", setvar, *rest]:
            value = ""
            for i in rest:
                value = f"{value} {i}"
            admin_memory.admin_var[str(setvar)] = value.strip()
            return f"Done setting {str(setvar)} !"
        case [".get", var, *rest]:
            try:
                result = admin_memory.admin_var[str(var)]
                return f"isi dari {var} adalah {result}"
            except:
                return f"isi {var} tidak ada!"
        case [".list"]:
            result = admin_memory.admin_var.keys()
            return f"variabel yg ada : {result}"        
        case [".sd", *rest]:
            return sd.buat_gambar(prompt=" ".join(rest))
        
        case [".1", *rest]:
            return set_sys_var('_s1', rest)
        case [".2", *rest]:
            return set_sys_var('_s2', rest)
        case [".3", *rest]:
            return set_sys_var('_s3', rest)
        case [".4", *rest]:
            return set_sys_var('_s4', rest)
        case [".5", *rest]:
            return set_sys_var('_s5', rest)
        case [".6", *rest]:
            return set_sys_var('_s6', rest)
        case [".7", *rest]:
            return set_sys_var('_s7', rest)
        case [".8", *rest]:
            return set_sys_var('_s8', rest)
        case [".9", *rest]:
            return set_sys_var('_s9', rest)
        case [".10", *rest]:
            return set_sys_var('_s10', rest)
        case [".11", *rest]:
            return set_sys_var('_s11', rest)
        case [".12", *rest]:
            return set_sys_var('_s12', rest)
        case [".13", *rest]:
            return set_sys_var('_s13', rest)
        case [".14", *rest]:
            return set_sys_var('_s14', rest)
        case [".15", *rest]:
            return set_sys_var('_s15', rest)
        case ["..", *rest]:
            msg_text = build_from_sysvars(" ".join(rest))
            result = await api.ask_gpt(msg_proc, conv_obj, msg_text)
            result = f"{result}\n\n\U0001F4CA".strip()


    nama_bot = conv_obj.bot_name.lower()
    awalan = msg_text[:len(nama_bot)].lower()
    if awalan == nama_bot:
        msg_text = msg_text[len(conv_obj.bot_name):].strip()


    # BOT COMMANDS
    msgcommand = shlex.split(msg_text.lower())
    match msgcommand:
        case ['eta', *rest]:
            return eta(conv_obj)
        case ['file', filename]:
            return f'{filename} is the filename'
        case ['set', param1, param2]:
            return f'{param1} is set to {param2}'
        case ['pdf', *rest]:
            response = ask_pdf('./BBB.pdf', " ".join(rest))
            insert_conv(conv_obj.user_number,
                        conv_obj.bot_number,
                        int(datetime.datetime.utcnow().timestamp()), 
                        response, cfg['CONFIG']['DB_FILE'])
            return response            
        case ['cari', *rest]:
            response = ask_lc(" ".join(rest))
            insert_conv(conv_obj.user_number,
                        conv_obj.bot_number,
                        int(datetime.datetime.utcnow().timestamp()), 
                        response, cfg['CONFIG']['DB_FILE'])
            return response        
        case ['gambar', *rest]:
            print(" ".join(rest))
            response = ask_dalle(conv_obj, " ".join(rest))
            return response
        case _ :
            result = await api.ask_gpt(msg_proc, conv_obj, msg_text)
            result = f"{result}\n\n\u2764".strip()
            return result 



def build_prompt() -> str:
    prompt_build = ""
    for i in range(1,11):
        if str(i) in admin_memory.admin_var:
            prompt_build = f"{prompt_build} {admin_memory.admin_var[str(i)]}" 
    return prompt_build

def build_from_sysvars(prompt):
    syslist = ['_s1', '_s2','_s3','_s4','_s5','_s6','_s7','_s8','_s9','_s10','_s11','_s12','_s13','_s14','_s15',]
    result = ""
    for i in syslist:
        try:
            result = result + admin_memory.admin_var[i] + "\n\n"
        except:
            pass
    return f"{prompt}\n\n{result}"

async def notify_admin(message: str):
    for i in cfg['CONFIG']['ADMIN_NUMBER']:
        result = await send_to_phone(i, cfg['CONFIG']['BOT_NUMBER'], message)
    return result

async def send_to_phone(user_number: str, bot_number: str, message: str):
    """send langsung ke WA, tapi ke *user_number*, bukan ke bot_number"""
    message = {
        "message": message, # Replace with your message text
        "from": bot_number, # Replace with the sender number
        "to": user_number # Replace with out bot number
    } # type: ignore

    response = requests.post(cfg['WHATSAPP']['SEND_URL'], json=message)

    if response.status_code == 200:
        return "Message sent successfully!"
    else:
        return f"Error sending message. Status code: {response.status_code}"

def ask_dalle():
    pass