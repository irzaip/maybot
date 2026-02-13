import ollama
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def check_ollama_response(prompt: str, reference_content: str, threshold: float = 0.7) -> bool:
    """
    Menggunakan Ollama untuk menghasilkan jawaban dan memeriksa kesesuaiannya dengan konten referensi.
    
    :param prompt: Pertanyaan atau perintah untuk Ollama.
    :param reference_content: Konten yang dijadikan acuan.
    :param threshold: Batas kemiripan minimum agar dianggap sesuai.
    :return: True jika jawaban cukup sesuai, False jika tidak.
    """
    
    # Panggil model Ollama
    response = ollama.chat("qwen2.5:14b", messages=[{"role": "user", "content": prompt}])
    generated_answer = response["message"]["content"]
    
    # Hitung kesamaan dengan cosine similarity
    vectorizer = TfidfVectorizer().fit_transform([generated_answer, reference_content])
    similarity = cosine_similarity(vectorizer[0], vectorizer[1])[0][0]
    
    return similarity >= threshold

# Contoh penggunaan
prompt = "Gandjila adalah refleksi dari keganjilan"
reference = "Gandjila adalah refleksi faham keganjilan."
result = check_ollama_response(prompt, reference)
print("Jawaban sesuai:", result)
