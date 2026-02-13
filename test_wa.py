#!/usr/bin/env python3
"""
Test Koneksi ke Endpoint /messages di wa.py
Script untuk chatting dengan bot MayBot via API
"""

import requests
import json
import sys
import time
from typing import Optional

SERVER_URL = "http://192.168.30.50:8998"
MESSAGES_ENDPOINT = f"{SERVER_URL}/messages"
SPECIAL_MESSAGES_ENDPOINT = f"{SERVER_URL}/special_messages"

BOT_NUMBER = "6285775300227@c.us"
DEFAULT_USER_NUMBER = "6281234567890@c.us"

def send_message(
    message: str,
    user_number: str,
    bot_number: str = BOT_NUMBER,
    endpoint: str = "messages",
    notifyName: str = "",
    message_type: str = "chat"
) -> dict:
    """Kirim pesan ke endpoint /messages atau /special_messages."""
    
    payload = {
        "text": message,
        "user_number": user_number,
        "bot_number": bot_number,
        "timestamp": int(time.time()),
        "notifyName": notifyName,
        "type": message_type,
        "client": "whatsapp",
        "author": "",
        "hasMedia": False,
        "message": {}
    }
    
    target_endpoint = MESSAGES_ENDPOINT if endpoint == "messages" else SPECIAL_MESSAGES_ENDPOINT
    
    try:
        response = requests.post(
            target_endpoint,
            json=payload,
            timeout=60
        )
        
        data = response.json()
        
        if response.ok:
            print(f"✅ Berhasil!")
            print(f"Response: {data}")
            return data
        else:
            print(f"❌ Error: {data.get('detail', data)}")
            return {}
            
    except requests.exceptions.ConnectionError:
        print("❌ Gagal terhubung ke server wa.py. Pastikan server berjalan.")
        return {}
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return {}

def chat_loop():
    """Main chat loop dengan input teks langsung."""
    
    print("=" * 50)
    print("🤖 TEST /MESSAGES ENDPOINT - MAYBOT")
    print("=" * 50)
    print("Ketik 'quit' atau 'exit' untuk keluar")
    print("Ketik 'switch' untuk beralih antara /messages dan /special_messages")
    print("Ketik 'user <nomor>' untuk ganti nomor user")
    print("-" * 50)
    
    current_endpoint = "messages"
    user_number = DEFAULT_USER_NUMBER
    
    while True:
        try:
            user_input = input(f"\n👤 [{user_number}] ({current_endpoint}): ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'keluar']:
                print("\n👋 Selamat tinggal!")
                break
            
            elif user_input.lower() == 'switch':
                current_endpoint = "special_messages" if current_endpoint == "messages" else "messages"
                print(f"\n🔄 Beralih ke endpoint: /{current_endpoint}")
                continue
            
            elif user_input.lower().startswith('user '):
                new_number = user_input[5:].strip()
                if new_number:
                    user_number = new_number if '@' in new_number else f"{new_number}@c.us"
                    print(f"\n👤 Nomor user changed to: {user_number}")
                else:
                    print("\n❌ Nomor tidak valid")
                continue
            
            elif user_input.lower() == 'status':
                print(f"\n📋 Status:")
                print(f"   User: {user_number}")
                print(f"   Bot: {BOT_NUMBER}")
                print(f"   Endpoint: /{current_endpoint}")
                continue
            
            else:
                print("\n⏳ Sedang memproses...")
                result = send_message(
                    message=user_input,
                    user_number=user_number,
                    bot_number=BOT_NUMBER,
                    endpoint=current_endpoint
                )
                    
        except KeyboardInterrupt:
            print("\n\n👋 Program dihentikan.")
            break
        except EOFError:
            print("\n\n👋 Input selesai.")
            break

def single_message_test():
    """Test kirim pesan tunggal."""
    print("\n📤 Test: Pesan Tunggal")
    print("-" * 30)
    send_message(
        message="Halo, ini pesan test dari Python!",
        user_number="6281234567890@c.us"
    )

def conversation_test():
    """Test kelanjutan percakapan."""
    print("\n📝 Test: Percakapan Berkelanjutan")
    print("-" * 30)
    
    user_number = "6281234567890@c.us"
    
    print("\n📤 Pesan 1: Halo, siapa kamu?")
    result1 = send_message(
        message="Halo, siapa kamu?",
        user_number=user_number
    )
    
    print("\n📤 Pesan 2: Apa yang bisa kamu lakukan?")
    result2 = send_message(
        message="Apa yang bisa kamu lakukan?",
        user_number=user_number
    )
    
    print("\n📤 Pesan 3: Ceritakan tentang cuaca")
    result3 = send_message(
        message="Ceritakan tentang cuaca",
        user_number=user_number
    )

def special_messages_test():
    """Test endpoint /special_messages."""
    print("\n�_special_messages")
    print("-" * 30)
    
    user_number = "6281234567890@c.us"
    
    print("\n📤 Pesan 1 via /special_messages")
    result1 = send_message(
        message="Halo dari special messages!",
        user_number=user_number,
        endpoint="special_messages"
    )

def persona_test():
    """Test dengan berbagai persona."""
    print("\n🎭 Test: Berbagai Persona")
    print("-" * 30)
    
    user_number = "6281234567890@c.us"
    
    personas = ["ASSISTANT", "SALES_CS", "HRD"]
    
    for i, persona in enumerate(personas):
        print(f"\n📤 Pesan dengan persona {persona}:")
        result = send_message(
            message=f"Test message #{i+1} untuk persona {persona}",
            user_number=user_number
        )

def main():
    """Main function dengan menu pilihan."""
    print("=" * 50)
    print("🤖 MAYBOT API TESTER - /messages ENDPOINT")
    print("=" * 50)
    print("Pilih mode:")
    print("1. Chat Interaktif")
    print("2. Test Pesan Tunggal")
    print("3. Test Percakapan Berkelanjutan")
    print("4. Test /special_messages")
    print("5. Test Berbagai Persona")
    print("6. Keluar")
    print("-" * 50)
    
    choice = input("Masukkan pilihan [1-6]: ").strip()
    
    if choice == '1':
        chat_loop()
    elif choice == '2':
        single_message_test()
    elif choice == '3':
        conversation_test()
    elif choice == '4':
        special_messages_test()
    elif choice == '5':
        persona_test()
    elif choice == '6':
        print("👋 Selamat tinggal!")
    else:
        print("❌ Pilihan tidak valid.")

if __name__ == "__main__":
    main()
