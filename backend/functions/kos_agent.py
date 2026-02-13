import requests
import json
import re

mydata = '''
-----
AZANA KOST
Kos-kosan bersih dan nyaman dengan akses mudah ke lokasi-lokasi strategis di Jakarta Selatan.
Fasilitas yang tersedia Kamar Mandi dalam, AC, Perabot, laundry dan Housekeeping, Internet WIFI. Cocok untuk pegawai
kantoran dan pebisnis. Murah dan nyaman. Parkir kost tersedia, namun tidak direkomendasi. Laundry tidak termasuk. Water heater tidak ada.

Kos-kosan berlokasi dengan akses mudah ke kawasan Sudirman Central Business District (SCBD)
dan Gatot Subroto (Gatsu). Dekat dengan Halte Busway Polda (Polda Metro Jaya), Komdak,
Wolter Mongonsidi, Santa, Tendean, Gunawarman, Ritz Carlton, Pacific place, Kantor Pajak,
Telkom, Blok S, Bank Mandiri, Medco Graha Energi (Graha Energy Medco), Graha Niaga, LIPI,
Artha Graha, Senayan, Kompleks Menteri Widya Chandra, Bursa Efek Jakarta (BEJ), Semanggi dan Senopati.

Berapa harga kamar?
Masih ada kamar tersedia, bpk/ibu. Harga kamar ada yang 2.5 jt ada yg 3 jt. 
Perbedaan harga karena luas kamar dan view kamar. Ukuran kamar sekitar 12m-14m persegi.
Di setiap kamar ada kamar mandi dalam.

Berapa kamar sekarang yang available?
satu kamar yang harga 3 jt / bulan

Alamat lengkap: Jl. Tulodong Bawah I No.16, RT.3/RW.1,
    Senayan, Kec. Kby. Baru, Kota Jakarta Selatan,
    Daerah Khusus Ibukota Jakarta 12190

Telepon (informasi): 0895-3522-77562

buat lokasi kami bisa menggunakan map ini:
https://goo.gl/U7duAc


Untuk foto kamar, bisa lihat di url:
https://goo.gl/ELR7rh

Kos kami menerima pria ataupun wanita sebagai pelanggan, namun kami bukan kosan yang bebas.

Kamar hanya di peruntukkan satu orang, dan tidak diperkenankan membawa pasangan ke kamar.
Pasangan yang berkunjung hanya bisa sebatas teras depan.

Tamu pelanggan tidak diperkenankan masuk ke kamar dan hanya boleh menerima tamu di ruang teras yang telah kami sediakan,juga tidak boleh memasak di kamar. Hewan peliharaan tidak diperkenankan di kos kami.
Tamu juga tidak boleh menginap, dan masuk ke area pelanggan. Tamu hanya di teras depan.

Buat booking dan info ketersediaan kamar secara perinci bisa hubungi ke nomor kami yang ini. Maaf kalau slow respond

Saran kami ialah mensurvey terlebih dahulu ke lokasi baru kalau cocok setelah itu booking.

Untuk melihat ke lokasi bisa bertemu dengan mbak Tur, atau mas Riski. Silahkan datang di waktu jam kantor (8am - 8pm).

Untuk pendaftaran harus melengkapi form yg telah tersedia di tempat dan melengkapi persyaratannya, seperti fotokopi KTP / identitas dan persyaratan lainnya.
-----
'''

def build_task1(input):
    persona = '''Kamu adalah customer servis senior dari usaha kos-kosan Azana kost dan kamu menjawab dengan detail setiap pertanyaan.
    '''

    task1 ='''
Kamu bercakap-cakap dengan pelanggan yang sedang berminat untuk menempati sebuah kamar.

Pelanggan bertanya:
Selamat malam.

Jawaban kamu secara singkat dalam bahasa Indonesia adalah:
Selamat malam, ada yang kami bisa bantu?
lalu pelanggan bertanya lagi.
'''
    return f"{persona} {mydata} {task1}"


def build_task2(input):
    task2 = f'''
Anda adalah AI Quality Checker yang bertugas menilai kualitas suatu jawaban berdasarkan beberapa kriteria utama. 
Anda harus melakukan analisis mendalam terhadap jawaban yang diberikan dan mengembalikan hasil dalam format JSON.

Kriteria Penilaian:

Kebenaran (correctness) - Apakah jawaban tersebut faktual dan benar?

Kelengkapan (completeness) - Apakah jawaban mencakup semua aspek yang relevan?

Kejelasan (clarity) - Apakah jawaban ditulis dengan jelas dan mudah dipahami?

Relevansi (relevance) - Apakah jawaban sesuai dengan pertanyaan yang diberikan?

Gaya Bahasa (language style) - Apakah jawaban menggunakan bahasa yang sesuai (formal/informal, teknis/non-teknis)?

Struktur (structure) - Apakah jawaban memiliki susunan yang baik dan logis?

contoh jawaban: 

{{
  "correctness score": 10,
  "completeness score": 10,
  "clarity score": 10,
  "relevance score": 10,
  "language_style score": 10,
  "structure score": 10,
  "overall_score": 10,
  "final_feedback": "Ringkasan evaluasi beserta saran perbaikan jika ada."
}}

pertanyaan yang diajukan:
{input}

Dan kamu sebagai asisten ber-bahasa Indonesia akan membandingkan dengan data
{mydata}

Jawaban kamu adalah 
'''
    return f"{task2}"



def chat_with_ollama(model="qwen2.5:14b", system_prompt="", user_prompt="",
        api_url="http://localhost:11434/api/generate"):

    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": user_prompt,
        "system": system_prompt,
        "stream": False
    }

    response = requests.post(api_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:

        return response.json().get("response", "No response")
    else:
        return f"Error: {response.status_code}, {response.text}"

def extract_overall_score(text):
    # Ambil bagian JSON (support multi-line)
    match = re.search(r'\{.*?\}', text, re.DOTALL)
    
    if match:
        try:
            data = json.loads(match.group(0))
            return data.get("overall_score")
        except json.JSONDecodeError as e:
            print(f"Gagal parse JSON: {e}")
    
    return None

def ask_agent(user_prompt):
    response = chat_with_ollama(system_prompt=build_task1(user_prompt), user_prompt=user_prompt)
    print("\n\nOllama:", response)

    check = chat_with_ollama(system_prompt=build_task2(user_prompt), user_prompt=user_prompt)
    score=extract_overall_score(check)
    print(score)

    return {"response": response, "score": score}

if __name__ == "__main__":
    system_prompt = "Anda adalah asisten AI yang membantu menjawab pertanyaan dengan jelas dan ringkas."
    while True:
        user_prompt = input("Anda: ")
        pertanyaan = user_prompt
        if user_prompt.lower() in ["exit", "quit", "keluar"]:
            print("Mengakhiri chat...")
            break
        
        ask_agent(user_prompt)
