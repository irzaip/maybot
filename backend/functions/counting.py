from backend.conversations import Conversation

def tambah_free_tries(conv_obj: Conversation, jumlah: int = 5):
    pass

def kurangi_profanity_counter(conv_obj: Conversation):
    pass

def kurangi_funny_counter(conv_obj: Conversation):
    pass

def kurangi_promo_counter(conv_obj: Conversation):
    pass

def kurangi_free_tries(conv_obj: Conversation):
    pass

def tambah_paid_messages(conv_obj: Conversation, jumlah: int = 5):
    conv_obj.paid_messages += jumlah

def kurangi_paid_messages(conv_obj: Conversation) -> None:
    conv_obj.paid_messages -= 1
    if conv_obj.paid_messages < 0:
        conv_obj.paid_messages = 0

def pra_proses(conv_obj: Conversation):
    pass
