from backend.conversations import Conversation, Message, ConvMode, Persona, ConvType
import sqlite3
import toml
from typing import Union
from backend import db_oper as dbo
from backend.functions import admin_func as admin
from backend.functions import demo_func as demo
from backend.functions import friend_func as friend
from backend import ollama_api as api
from backend.functions import counting as ct
from backend.functions import interview as iv
from backend.functions import gold_func as gold
from backend.functions import platinum_func as platinum
from backend.functions import persona_func as pf
from backend.functions import kos_agent as cs
from backend.functions import sd_agent as sd
import pprint

#from queue import Queue
import asyncio
from colorama import Fore, Back, Style

cfg = toml.load('config.toml')



class MsgProcessor:
    def __init__(self, db_file: str) -> None:
        self.name = "Process"
        #self.conv_obj = conv_obj
        self.queue = asyncio.Queue()
        self.queue2 = asyncio.Queue()
        self.response = ""
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()
        self.antrian1 = 0
        self.antrian2 = 0
        self.on_maintenance = False

    def is_bot(self, message: Message) -> bool:
        bot_number = cfg['CONFIG']['BOT_NUMBER']
        if (message.user_number == bot_number):
            return True
        return False
    
    def is_admin(self, message: Message) -> bool:
        admin_number = cfg['CONFIG']['ADMIN_NUMBER']
        if (message.user_number in admin_number) or (message.author in admin_number):
            return True
        return False

    def is_human_user(self, message: Message) -> bool:
        if ("@c.us" in message.user_number):
            return True
        return False
    
    def is_group(self, message: Message) -> bool:
        if ("@g.us" in message.user_number):
            return True
        return False
        
    def is_StartWithBotName(self, conv_obj: Conversation,  message: Message) -> bool:
        if message.text[:len(conv_obj.bot_name)].lower() == conv_obj.bot_name:
            return True
        return False        

    def pre_process(self, conv_obj: Conversation, message: Message):
        pass
        
    #LOOP TIKET UNTUK OOBA - tidur 2 detik tapi antri
    async def process_queue_ooba(self):
        while True:
            try:
                tiket = await self.queue2.get()
                print(f'panggilan untuk antrian {tiket} !!')
                await asyncio.sleep(2)
            except:
                print(f'tidak ada antrian')
                await asyncio.sleep(0.01)
                self.queue.task_done()


    #LOOP TIKET UNTUK CHATGPT - tidur 20 detik antar request
    async def process_queue_gpt(self):
        while True:
            try:
                tiket = await self.queue.get()
                print(f'panggilan untuk antrian {tiket} !!')
                await asyncio.sleep(20)
            except:
                print(f'tidak ada antrian')
                await asyncio.sleep(0.01)
                self.queue.task_done()

    def is_ignored(self, message: Message):
        if (message.author in cfg['IGNORE']['IGNORE']) or (message.user_number in cfg['IGNORE']['IGNORE']):
            return True
        else:
            return False

    async def process(self, conv_obj: Conversation, message: Message) -> Union[str, None, str]:
        """Prosedur ini memproses Terima pesan dari WA"""
        #ct.pra_proses(conv_obj)
        print(f"{Fore.YELLOW}Got BOT:{conv_obj.bot_number} - USER NUMBER:{conv_obj.user_number}({conv_obj.user_name})")
        print(f"Message: {message.text}")
        print( f"{Fore.LIGHTMAGENTA_EX}ct:{conv_obj.convtype}{Style.RESET_ALL}")
            
        nama_bot = conv_obj.bot_name.lower()
        awalan = message.text[:len(nama_bot)].lower()

        #ADMIN COMMAND.
        if self.is_admin(message) and (nama_bot == awalan):
            return await admin.run(self, conv_obj, message.text) 

        if message.text.startswith('.'):
            if self.is_admin(message):
                return await admin.run(self, conv_obj, message.text)

        if "konfirmasi" in message.text.lower():
            if message.author:
                await admin.notify_admin(f'INFO: konfirmasi signal from group {message.user_number} or {message.author}')
            else:
                await admin.notify_admin(f'INFO: konfirmasi signal at japrian {message.user_number}')

        if "info_cs" in message.text.lower():
            conv_obj.persona = Persona.ASSISTANT
            pf.set_persona(Persona.SALES_CS, conv_obj)
            print(f'{Fore.RED}{Back.WHITE}INFO: ADA SIGNAL INFO_CS DARI {message.user_number}{Fore.RESET}{Back.RESET}')
            await admin.notify_admin(f'INFO: signal INFO_CS dari user {message.user_number}')
            dbo.insert_info_cs(conv_obj.user_number, int(message.timestamp), cfg['CONFIG']['DB_FILE'])
            return cfg['SALES_CS']['GREETING']
        
        #potong awalan
        if awalan == nama_bot:
            message.text = message.text[len(conv_obj.bot_name):].strip()

        #ignore looping error admin notif send
        if message.text.lower().startswith("ada error") or message.text.lower().startswith("INFO:"):
            return None

        # PRA PROCESSING MESSAGE - buang aja karakter unicode dan quote
        message.text = str(message.text)
        message.text = message.text.encode('ascii', errors='ignore').decode()
        message.text = message.text.replace("'"," ").replace('"',' ')


        print("-------------------------------------------------")
        print(f"{Fore.GREEN}{Style.BRIGHT}Message:",message)
        print(f"{Style.RESET_ALL}-------------------------------------------------")

        # KOS_CS Persona - use kos_agent
        if conv_obj.persona == Persona.KOS_CS:
            print(f"{Fore.CYAN}>>> Using KOS_CS agent{Style.RESET_ALL}")
            response = cs.ask_agent(message.text)
            if response and isinstance(response, dict):
                score = response.get('score', 0)
                try:
                    score_val = float(score) if score else 0
                    if score_val < 5:
                        print(f'{Fore.RED}{Back.WHITE}LOW SCORE: {score} - {message.user_number}{Fore.RESET}{Back.RESET}')
                        try:
                            await admin.notify_admin(f'LOW SCORE {score} - {message.user_number}\n\n{message.text}\n\n{response["response"]}')
                        except:
                            pass
                except (ValueError, TypeError):
                    pass
            return response.get('response', 'Maaf, ada kesalahan.') if response else 'Maaf, ada kesalahan.'

        if conv_obj.convtype == ConvType.ADMIN:
            return await admin.run(self, conv_obj, message.text) 

        if conv_obj.convtype == ConvType.PLATINUM:
            return await platinum.run(self, conv_obj, message)

        if conv_obj.convtype == ConvType.GOLD:
            return await gold.run(self, conv_obj, message)

        if conv_obj.convtype == ConvType.FRIEND:
            return await friend.run(self, conv_obj, message)

        if conv_obj.convtype == ConvType.DEMO:
            return await demo.run(self, conv_obj, message)

        # PROCESS BY PERSONA AND MODE
        if conv_obj.convmode == ConvMode.YESNO:
            if "y" in message.text.lower():
                return "Kamu menjawab ya"
            if "t" in message.text.lower():
                return "Kamu menjawab tidak"

        if conv_obj.convmode == ConvMode.ASK:
            if "ok" in message.text.lower():
                return "oke juga"

        # JUST RETURN IT
        return "pfft..."


if __name__ == '__main__':
    pass