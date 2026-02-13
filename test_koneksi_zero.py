#!/usr/bin/env python3
"""
Test Koneksi ke Agent Zero External API
Script untuk chatting dengan Agent Zero via API
"""

import requests
import json
import sys
import base64
from typing import Optional

API_URL = "http://localhost:32768/api_message"
API_KEY = "62D9d6ENLvUImDRH"

headers = {
    "Content-Type": "application/json",
    "X-API-KEY": API_KEY
}

context_id: Optional[str] = None

def send_message(
    message: str,
    context_id: Optional[str] = None,
    lifetime_hours: int = 24,
    project: Optional[str] = None,
    attachments: Optional[list] = None
) -> dict:
    """Kirim pesan ke Agent Zero."""
    payload = {
        "message": message,
        "lifetime_hours": lifetime_hours
    }
    
    if context_id:
        payload["context_id"] = context_id
    
    if project:
        payload["project"] = project
    
    if attachments:
        payload["attachments"] = attachments
    
    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        data = response.json()
        
        if response.ok:
            print(f"✅ Berhasil!")
            print(f"Response: {data.get('response', 'N/A')}")
            if data.get('context_id'):
                print(f"Context ID: {data.get('context_id')}")
            return data
        else:
            print(f"❌ Error: {data.get('error', 'Unknown error')}")
            return {}
            
    except requests.exceptions.ConnectionError:
        print("❌ Gagal terhubung ke Agent Zero. Pastikan server berjalan.")
        return {}
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return {}

def chat_loop():
    """Main chat loop dengan input teks langsung."""
    global context_id
    
    print("=" * 50)
    print("🤖 TEST KONEKSI AGENT ZERO")
    print("=" * 50)
    print("Ketik 'quit' atau 'exit' untuk keluar")
    print("Ketik 'new' untuk memulai percakapan baru")
    print("Ketik 'status' untuk melihat context ID saat ini")
    print("-" * 50)
    
    while True:
        try:
            user_input = input("\n👤 Anda: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'keluar']:
                print("\n👋 Selamat tinggal!")
                break
            
            elif user_input.lower() == 'new':
                context_id = None
                print("\n🔄 Percakapan baru dimulai...")
                continue
            
            elif user_input.lower() == 'status':
                print(f"\n📋 Context ID: {context_id if context_id else 'Belum ada'}")
                continue
            
            else:
                print("\n⏳ Agent Zero sedang mengetik...")
                result = send_message(user_input, context_id)
                
                if result and result.get('context_id'):
                    context_id = result['context_id']
                    
        except KeyboardInterrupt:
            print("\n\n👋 Programm dihentikan.")
            break
        except EOFError:
            print("\n\n👋 Input selesai.")
            break

def single_message_test():
    """Test kirim pesan tunggal."""
    print("\n📤 Test: Pesan Tunggal")
    print("-" * 30)
    send_message("Halo, ini pesan test dari Python!")

def conversation_test():
    """Test kelanjutan percakapan."""
    print("\n📝 Test: Kelanjutan Percakapan")
    print("-" * 30)
    
    global context_id
    
    result1 = send_message("Hai, siapa namamu?", lifetime_hours=24)
    
    if result1.get('context_id'):
        context_id = result1['context_id']
        
        print("\n📤 Mengirim pertanyaan kedua...")
        result2 = send_message("Apa yang bisa kamu lakukan?", context_id=context_id)
        
        if result2.get('context_id'):
            context_id = result2['context_id']
            
            print("\n📤 Mengirim pertanyaan ketiga...")
            result3 = send_message("Ceritakan tentang cuaca hari ini.", context_id=context_id)

def attachment_test():
    """Test kirim pesan dengan lampiran."""
    print("\n📎 Test: Pesan dengan Lampiran")
    print("-" * 30)
    
    text_content = "Hello World dari lampiran!"
    base64_content = base64.b64encode(text_content.encode()).decode()
    
    send_message(
        message="Please analyze this file:",
        attachments=[{
            "filename": "document.txt",
            "base64": base64_content
        }],
        lifetime_hours=12
    )

def main():
    """Main function dengan menu pilihan."""
    print("=" * 50)
    print("🤖 AGENT ZERO API TESTER")
    print("=" * 50)
    print("Pilih mode:")
    print("1. Chat Interaktif")
    print("2. Test Pesan Tunggal")
    print("3. Test Percakapan Berkelanjutan")
    print("4. Test Lampiran")
    print("5. Keluar")
    print("-" * 50)
    
    choice = input("Masukkan pilihan [1-5]: ").strip()
    
    if choice == '1':
        chat_loop()
    elif choice == '2':
        single_message_test()
    elif choice == '3':
        conversation_test()
    elif choice == '4':
        attachment_test()
    elif choice == '5':
        print("👋 Selamat tinggal!")
    else:
        print("❌ Pilihan tidak valid.")

if __name__ == "__main__":
    main()
