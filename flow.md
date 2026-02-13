# MayBot Flow Documentation

Dokumentasi alur kerja sistem MayBot dari pesan masuk hingga response ke WhatsApp.

---

## Overview

MayBot adalah chatbot WhatsApp yang menggunakan:
- **FastAPI** untuk web server
- **Ollama** untuk AI processing (local LLM)
- **SQLite** untuk database
- **WhatsApp-web.js** untuk koneksi WhatsApp

---

## Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          MAYBOT SYSTEM                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────┐     ┌─────────────────┐     ┌──────────────────┐   │
│  │   WhatsApp    │────▶│  waworks/       │────▶│   wa.py (FastAPI) │   │
│  │   User       │     │  index.js       │     │   Port 8998       │   │
│  └──────────────┘     └─────────────────┘     └────────┬─────────┘   │
│                                                          │             │
│                         ┌────────────────┐               │             │
│                         │  config.toml   │◀──────────────┘             │
│                         │  (konfigurasi) │                              │
│                         └────────────────┘                              │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                     backend/ (Python)                            │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │    │
│  │  │  Msgproc.py │  │ functions/   │  │ agents/                  │ │    │
│  │  │  (router)   │  │ *.py         │  │ agent1.py - agent8.py    │ │    │
│  │  └──────┬──────┘  └──────┬──────┘  └─────────────────────────┘ │    │
│  │         │                 │                                      │    │
│  │  ┌──────┴──────┐  ┌──────┴──────┐                              │    │
│  │  │ ollama_api.py│  │   db_oper.py │                              │    │
│  │  │  (LLM API)  │  │  (database)  │                              │    │
│  │  └──────┬──────┘  └───────────────┘                              │    │
│  └─────────┼─────────────────────────────────────────────────────────┘    │
│            │                                                           │
│  ┌─────────┴───────────┐                                              │
│  │  backend/data/      │                                              │
│  │  cipibot.db         │                                              │
│  │  (SQLite)           │                                              │
│  └─────────────────────┘                                              │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Ollama Server                                                   │    │
│  │  http://localhost:11434                                          │    │
│  │  Model: qwen2.5:14b (default)                                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Alur Utama: Pesan Masuk hingga Response

### Diagram Alur Pesan

```
┌─────────────┐
│ WhatsApp    │
│ User        │
└──────┬──────┘
       │
       │ 1. User mengirim pesan
       ▼
┌─────────────────────────┐
│ waworks/index.js       │
│ (WhatsApp-web.js)     │
└───────────┬─────────────┘
            │
            │ 2. axios.post('/messages')
            │    dengan JSON body:
            │    {
            │      text: "Halo",
            │      user_number: "628xxx@c.us",
            │      bot_number: "628yyy@c.us",
            │      timestamp: 1234567890,
            │      type: "chat",
            │      ...
            │    }
            ▼
┌─────────────────────────┐
│ wa.py                   │
│ @app.post("/messages")  │
└───────────┬─────────────┘
            │
            │ 3. Parse JSON
            │    Buat Message object
            │    panggil msgprocess.process()
            ▼
┌─────────────────────────┐
│ backend/Msgproc.py     │
│ async def process()    │
└───────────┬─────────────┘
            │
            │ 4. Cek convtype
            │    (DEMO, GOLD, FRIEND, PLATINUM)
            ▼
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌────────┐    ┌───────────┐
│ demo.  │    │ gold.     │
│ run()  │    │ run()     │
└────┬───┘    └─────┬─────┘
     │               │
     │    ┌─────────┴─────────┐
     │    │                     │
     ▼    ▼                     ▼
┌─────────────────────────────┐
│ backend/ollama_api.py      │
│ async def ask_gpt()        │
└───────────┬─────────────┘
            │
            │ 5. Insert ke DB
            │    db.insert_conv()
            │
            │ 6. Trim message
            │    rd.trim_msg()
            │
            │ 7. Append ke conversation
            │    conv_obj.messages.append()
            │
            │ 8. Kirim ke Ollama
            │    chat(model='qwen2.5:14b', messages=...)
            │
            │ 9. Parse response
            │    response.message.content
            ▼
┌─────────────────────────┐
│ Return response text    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ wa.py                   │
│ return {"message": "..."}│
└───────────┬─────────────┘
            │
            │ 10. JSON response ke index.js
            ▼
┌─────────────────────────┐
│ waworks/index.js       │
│ handleWaResponse()     │
│ chat.sendMessage()     │
└───────────┬─────────┘
            │
            ▼
    ┌─────────────────┐
    │ WhatsApp User  │
    │ Menerima pesan │
    └─────────────────┘
```

---

## Detail per File

### 1. waworks/index.js

**Lokasi:** `H:\PYTHON\waworks\index.js`

**Fungsi:** Klien WhatsApp menggunakan whatsapp-web.js

**Alur:**
```javascript
// Event listener untuk pesan masuk
client.on('message', async (msg) => {
  // 1. Skip pesan dengan type non-chat
  const skipTypes = ['e2e_notification', 'call_log', 'protocol', ...];
  if (skipTypes.includes(msg.type)) return;

  // 2. Ambil data dari pesan
  const requestData = {
    text: msg.body,
    user_number: msg.from,
    bot_number: msg.to,
    timestamp: msg.timestamp,
    notifyName: msg._data.notifyName || "",
    type: msg.type,
    client: "whatsapp",
    author: msg.author || "",
    hasMedia: msg.hasMedia,
    message: {}
  };

  // 3. Kirim ke endpoint /messages
  const response = await axios.post('http://192.168.30.50:8998/messages', requestData);

  // 4. Kirim response ke WhatsApp
  const chat = await client.getChatById(msg.from);
  await handleWaResponse(chat, response);
});
```

**Key Functions:**
| Function | Deskripsi |
|----------|-----------|
| `handleWaResponse()` | Parse response dan kirim ke WhatsApp |

---

### 2. wa.py

**Lokasi:** `H:\PYTHON\maybot\wa.py`

**Fungsi:** FastAPI server dengan endpoint `/messages`

**Endpoint `/messages` (line ~590):**
```python
@app.post("/messages")
async def receive_message(request: Request) -> dict:
    """
    Endpoint utama menerima pesan dari WhatsApp
    """
    # 1. Parse JSON dari request
    data = await request.json()

    # 2. Ekstrak field
    text = data.get("text", "")
    user_number = data.get("user_number", "")
    bot_number = data.get("bot_number", "")
    # ... field lainnya

    # 3. Validasi
    if not user_number or not text:
        return {"message": "Missing user_number or text"}

    # 4. Buat/add conversation object
    if user_number not in conversations:
        add_conversation(user_number=user_number, bot_number=bot_number)

    # 5. Buat Message object
    msg_obj = Message(
        text=text,
        user_number=user_number,
        bot_number=bot_number,
        # ... field lainnya
    )

    # 6. Proses melalui MsgProcessor
    response_text = await msgprocess.process(conversation_obj, message=msg_obj)

    # 7. Update database
    update_db_connection(...)

    # 8. Return response
    return {"message": str(response_text)}
```

**Variabel Global:**
| Variabel | Deskripsi |
|----------|-----------|
| `conversations` | Dict menyimpan Conversation object per user |
| `msgprocess` | Instance MsgProcessor |
| `DB_PATH` | Path ke database (`backend/data/cipibot.db`) |

---

### 3. backend/Msgproc.py

**Lokasi:** `H:\PYTHON\maybot\backend\Msgproc.py`

**Fungsi:** Router pesan ke function yang sesuai berdasarkan convtype

**Main Function `process()`:**
```python
async def process(self, conv_obj: Conversation, message: Message):
    """
    Route pesan ke function sesuai convtype
    """
    # Cek convtype dan panggil function yang sesuai
    if conv_obj.convtype == ConvType.GOLD:
        return await gold.run(self, conv_obj, message)

    if conv_obj.convtype == ConvType.FRIEND:
        return await friend.run(self, conv_obj, message)

    if conv_obj.convtype == ConvType.DEMO:
        return await demo.run(self, conv_obj, message)

    # Default: return pfft...
    return "pfft..."
```

**ConvType Enum:**
```python
class ConvType(str, Enum):
    DEMO = auto()      # Mode demo
    FRIEND = auto()     # Mode teman chat
    GOLD = auto()       # Mode Gold user
    PLATINUM = auto()   # Mode Platinum user
    ADMIN = auto()      # Mode admin
```

---

### 4. backend/functions/demo_func.py

**Lokasi:** `H:\PYTHON\maybot\backend\functions\demo_func.py`

**Fungsi:** Proses pesan dalam mode DEMO

**Main Function `run()`:**
```python
async def run(self, conv_obj: Conversation, message: Message):
    """
    Proses pesan untuk mode DEMO
    """
    msg_text = message.text

    # Cek memory (apakah menggunakan history)
    if conv_obj.persona == Persona.VOLD:
        memory = False
    else:
        memory = True

    # Panggil API Ollama
    result = await api.ask_gpt(self, conv_obj, msg_text, memory=memory)

    return result
```

---

### 5. backend/ollama_api.py

**Lokasi:** `H:\PYTHON\maybot\backend\ollama_api.py`

**Fungsi:** Interface ke Ollama LLM server

**Main Function `ask_gpt()`:**
```python
async def ask_gpt(main_obj, conv_obj: Conversation, prompt: str,
                  memory: bool = True, write_db: bool = True) -> str:
    """
    Kirim prompt ke Ollama dan return response
    """
    # 1. Insert prompt ke database
    if write_db:
        db.insert_conv(conv_obj.user_number,
                      conv_obj.bot_number,
                      int(datetime.datetime.utcnow().timestamp()),
                      prompt,
                      DB_PATH)

    # 2. Queue management
    main_obj.antrian1 += 1
    while main_obj.queue.qsize() > 0:
        await asyncio.sleep(1)

    # 3. Trim message history
    conv_obj.messages = rd.trim_msg(conv_obj.messages)

    # 4. Append user message
    conv_obj.messages.append({"role": "user", "content": prompt})

    # 5. Kirim ke Ollama
    response: ChatResponse = chat(
        model='qwen2.5:14b',
        messages=conv_obj.messages
    )

    # 6. Parse response
    message = response.message.content

    # 7. Append assistant message
    if memory:
        conv_obj.messages.append({"role": "assistant", "content": message})
    else:
        conv_obj.messages.pop()

    # 8. Insert response ke database
    if write_db:
        db.insert_conv(...)

    return message
```

**Parameter:**
| Parameter | Tipe | Default | Deskripsi |
|----------|------|--------|-----------|
| `main_obj` | MsgProcessor | - | Instance MsgProcessor untuk queue |
| `conv_obj` | Conversation | - | Object conversation |
| `prompt` | str | - | Prompt user |
| `memory` | bool | True | Gunakan conversation history |
| `write_db` | bool | True | Simpan ke database |

---

### 6. backend/db_oper.py

**Lokasi:** `H:\PYTHON\maybot\backend\db_oper.py`

**Fungsi:** Operasi database SQLite

**Key Functions:**
```python
def insert_conv(user_number, bot_number, timestamp, content, db_name):
    """Insert pesan ke tabel CONVERSATION"""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO CONVERSATION (user_number, bot_number, timestamp, content) VALUES (?,?,?,?)",
        (user_number, bot_number, timestamp, content)
    )
    conn.commit()
    cursor.close()
    conn.close()

def get_db_connection(user_number, bot_number, db_name):
    """Ambil connection data dari tabel CONNECTION"""
    ...

def get_all_conversations_sql(limit=1000, offset=0, db_name=DB_PATH):
    """Ambil semua conversation dari tabel CONVERSATION"""
    ...

def get_conversation_messages(user_number, bot_number=None, limit=100, offset=0, db_name=DB_PATH):
    """Ambil pesan dari tabel CONVERSATION"""
    ...
```

**Database Schema:**
```sql
-- Tabel CONNECTION
CREATE TABLE CONNECTION (
    user_number TEXT NOT NULL,
    bot_number TEXT NOT NULL,
    value TEXT,
    PRIMARY KEY (user_number, bot_number)
);

-- Tabel CONVERSATION
CREATE TABLE CONVERSATION (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_number TEXT NOT NULL,
    bot_number TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    content TEXT NOT NULL
);
```

---

### 7. backend/functions/reduksi.py

**Lokasi:** `H:\PYTHON\maybot\backend\functions\reduksi.py`

**Fungsi:** Mengatur panjang conversation history

**Key Functions:**
```python
def count_words(input: str) -> int:
    """Hitung jumlah kata dalam string"""
    return len(input.split())

def hitung_total_kata(input: list):
    """Hitung total kata dalam list messages"""
    total = 0
    for i in input:
        hasil = count_words(i['content'])
        total += hasil
    return (len(input), total)

def trim_msg(messages: list) -> list:
    """
    Potong message history jika terlalu panjang
    Default limit: 800 kata
    """
    length, total = hitung_total_kata(messages)
    if total > 800:
        # Keep system messages dan half dari conversation
        sys_prom = messages[:3]
        trim_at = int(3 + (length / 2))
        messages = sys_prom + messages[trim_at:]
    return messages
```

---

### 8. backend/conversations.py

**Lokasi:** `H:\PYTHON\maybot\backend\conversations.py`

**Fungsi:** Model data untuk Conversation dan Message

**Class `Message`:**
```python
class Message(BaseModel):
    """Model pesan dari WhatsApp"""
    text: str
    user_number: str
    bot_number: str
    timestamp: int
    notifyName: str = ""
    type: str
    client: str
    author: str = ""
    hasMedia: bool = False
    message: dict = {}
```

**Class `Conversation`:**
```python
class Conversation():
    """Object conversation per user"""
    def __init__(self, user_number: str, bot_number: str):
        self.user_number = user_number
        self.bot_number = bot_number
        self.bot_name = "Maya"
        self.persona = Persona.ASSISTANT
        self.convmode = ConvMode.CHITCHAT
        self.convtype = ConvType.DEMO
        self.messages = []  # Conversation history
        self.free_tries = 5
        self.paid_messages = 0
        # ... many more attributes
```

---

### 9. config.toml

**Lokasi:** `H:\PYTHON\maybot\config.toml`

**Fungsi:** Konfigurasi global aplikasi

**Key Sections:**
```toml
[CONFIG]
LOGDIR = "./log/"
BOT_NUMBER = "628984633949@c.us"
ADMIN_NUMBER = ["62895352277562@c.us", "120363149813038443@g.us"]
DB_FILE = 'backend/data/cipibot.db'
MAX_TOKEN = 4192
WORD_LIMIT = 1000

[ASSISTANT]
M_S = "Kamu adalah Maya, Assisten yang baik..."
M_U = "Kamu akan menjadi teman dalam chat..."
M_A = "Halo, nama saya Maya..."

[FIT_TRAINER]
M_S = "Kamu adalah Maya, asisten kesehatan..."
M_U = "..."
M_A = "..."

[OLLAMA]
BASE_URL = "http://localhost:11434"
MODEL = "qwen2.5:14b"
```

---

## Persona System

Persona didefinisikan di `config.toml` dengan 3 komponen:

| Komponen | Key | Deskripsi |
|----------|-----|-----------|
| System | `M_S` | System prompt yang selalu ada di awal |
| User | `M_U` | Template untuk pesan user |
| Assistant | `M_A` | Template untuk response assistant |

**Contoh Persona ASSISTANT:**
```toml
[ASSISTANT]
M_S = "Kamu adalah Maya, Assisten yang baik..."
M_U = "Kamu akan menjadi teman dalam chat..."
M_A = "Halo, nama saya Maya..."
```

**Load Persona:**
```python
# Di persona_func.py
def set_persona(persona: Persona, conv_obj: Conversation):
    cf.reset_system(conv_obj)
    set_bot_name(conv_obj.bot_name, conv_obj)
    conv_obj.persona = persona.value
    cf.add_system(conv_obj, cfg[persona.name]['M_S'])
    cf.add_role_user(conv_obj, cfg[persona.name]['M_U'])
    cf.add_role_assistant(conv_obj, cfg[persona.name]['M_A'])
```

---

## Conversation Mode

**ConvMode Enum:**
```python
class ConvMode(str, Enum):
    CHITCHAT = auto()   # Chat biasa
    ASK = auto()        # Mode tanya-jawab
    THINK = auto()      # Mode berpikir
    QUIZ = auto()       # Mode kuis
    TIMED = auto()      # Mode timed
    INTERVIEW = auto()  # Mode interview
    YESNO = auto()      # Mode yes/no
    CHAIN = auto()      # Mode chain
```

---

## Sequence Diagram

```
Title: User sends message to bot

User->>index.js: Send "Halo Maya"
activate index.js
index.js->>wa.py: POST /messages {text: "Halo Maya", user_number: "xxx"}
activate wa.py
wa.py->>Msgproc: msgprocess.process(conv_obj, message)
activate Msgproc
Msgproc->>demo_func: demo.run(self, conv_obj, message)
activate demo_func
demo_func->>ollama_api: ask_gpt(self, conv_obj, "Halo Maya")
activate ollama_api
ollama_api->>reduksi: trim_msg(messages)
reduksi-->>ollama_api: trimmed messages
ollama_api->>db_oper: insert_conv(...)
db_oper-->>ollama_api: Done
ollama_api->>Ollama: chat(model="qwen2.5:14b", messages=[...])
activate Ollama
Ollama-->>ollama_api: response.message.content
ollama_api-->>demo_func: "Halo! Saya Maya..."
demo_func-->>Msgproc: response text
Msgproc-->>wa.py: response text
wa.py-->>index.js: {"message": "Halo! Saya Maya..."}
index.js->>User: sendMessage("Halo! Saya Maya...")
deactivate index.js
```

---

## File Structure

```
maybot/
├── wa.py                           # Main FastAPI app
├── config.toml                     # Configuration
├── requirements.txt               # Python dependencies
│
├── backend/
│   ├── __init__.py
│   ├── conversations.py           # Models (Message, Conversation)
│   ├── Msgproc.py                 # Message processor router
│   ├── ollama_api.py              # Ollama LLM interface
│   ├── db_oper.py                  # Database operations
│   │
│   ├── agents/                     # Agent implementations
│   │   ├── agent1.py - agent8.py
│   │   └── agent_info_cs.py
│   │
│   ├── functions/                  # Function modules
│   │   ├── admin_func.py
│   │   ├── demo_func.py
│   │   ├── friend_func.py
│   │   ├── gold_func.py
│   │   ├── platinum_func.py
│   │   ├── counting.py
│   │   ├── reduksi.py
│   │   ├── trans_id.py
│   │   ├── interview.py
│   │   ├── kos_agent.py
│   │   ├── sd_agent.py
│   │   └── apicall_.py
│   │
│   ├── utils/                      # Utility modules
│   │   ├── media_helpers.py
│   │   └── chat_ollama.py
│   │
│   └── data/                       # Database
│       ├── cipibot.db
│       └── cr.sql
│
├── frontend/                      # Vue.js Admin (development)
│
└── waworks/                       # WhatsApp-web.js client
    ├── index.js
    └── package.json
```

---

## API Endpoints

### POST /messages
Endpoint utama untuk menerima pesan dari WhatsApp.

**Request:**
```json
{
  "text": "Halo Maya",
  "user_number": "6285775300227@c.us",
  "bot_number": "628984633949@c.us",
  "timestamp": 1700000000,
  "notifyName": "John",
  "type": "chat",
  "client": "whatsapp",
  "author": "",
  "hasMedia": false,
  "message": {}
}
```

**Response:**
```json
{
  "message": "Halo! Saya Maya, ada yang bisa saya bantu?"
}
```

### GET /ping
Health check endpoint.

**Response:**
```json
{
  "message": "pong"
}
```

---

## Troubleshooting

### Error: "no such table: CONNECTION"
- Cause: Database tables belum dibuat
- Solution: Jalankan `python -c "exec(open('backend/data/cr.sql').read())"`

### Error: "ConnectionRefused" ke Ollama
- Cause: Ollama server tidak berjalan
- Solution: Jalankan `ollama serve`

### Error: 422 Unprocessable Entity
- Cause: Format JSON tidak sesuai dengan yang diharapkan
- Solution: Cek field yang dikirim, terutama `text`, `user_number`, `bot_number`

---

## Menjalankan Sistem

### 1. Jalankan Ollama
```bash
ollama serve
```

### 2. Jalankan wa.py (FastAPI)
```bash
uvicorn wa:app --port 8998 --host 192.168.30.50
```

### 3. Jalankan index.js (WhatsApp Client)
```bash
cd waworks
npm install
node index.js
```

### 4. Scan QR Code
QR code akan muncul di terminal index.js. Scan dengan WhatsApp untuk autentikasi.

---

## Credits

MayBot dibuat dengan teknologi:
- **FastAPI** - Web framework
- **Ollama** - Local LLM
- **WhatsApp-web.js** - WhatsApp API
- **SQLite** - Database
- **Vue.js** - Admin interface
