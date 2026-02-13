from backend.conversations import Conversation, ConvMode, Message
from colorama import Fore, Style, Back
import toml
import random
from backend.functions import counting as ct
#import apicall_ as api
import datetime
from backend.db_oper import insert_conv
import asyncio
from backend.functions import interview as iv
from typing import Literal

cfg = toml.load('config.toml')


async def run(self, conv_obj: Conversation, message: Message):
    return "NOT HAVING A GOLD USER"