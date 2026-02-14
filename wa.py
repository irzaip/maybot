from fastapi import FastAPI, Query, HTTPException, WebSocket, WebSocketDisconnect, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from backend.conversations import Message, BotQuestion, ConvMode, ConvType
from backend.conversations import MessageContent, Conversation, Persona
from backend.Msgproc import MsgProcessor
import requests, os, random, sys, json, sqlite3
from typing import List, Union, Dict, Any, Optional
import asyncio
import nest_asyncio
import random, string
import logging
from backend.db_oper import (
    new_db_connection,
    update_db_connection,
    get_db_all_connection,
    get_db_connection,
    get_conversation_messages,
    get_all_conversations_sql,
    get_conversation_count,
    insert_conv as dbo_insert_conv,
)
from backend.utils.media_helpers import make_media_response, encode_relative
import toml
from queue import Queue
from datetime import datetime
import uvicorn
from colorama import just_fix_windows_console, Fore, Back, Style
from backend.functions import counting as ct
from backend.functions import persona_func as pf
from backend.functions import conv_func as cf
from backend.functions import (
    admin_func,
    demo_func,
    friend_func,
    gold_func,
    platinum_func,
    reduksi,
    trans_id,
    interview,
    kos_agent,
    sd_agent,
    apicall_,
)
from backend.agents import (
#    agent1,
#    agent2,
#    agent3,
#    agent4,
 #   agent5,
 #   agent6,
 #   agent7,
 #   agent8,
    agent_info_cs,
)
from fastapi.middleware.cors import CORSMiddleware

AGENT_ZERO_URL = "http://localhost:32777/api_message"
AGENT_ZERO_API_KEY = "62D9d6ENLvUImDRH"


just_fix_windows_console()
cfg = toml.load("config.toml")

CONFIG = {}
# queue = Queue()
msgprocess = MsgProcessor(db_file="backend/data/cipibot.db")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=cfg["CONFIG"]["LOGDIR"] + "wa.log",
)

app = FastAPI()

origins = [
    "http://127.0.0.1",
    "http://127.0.0.1:5173",
    "http://localhost",
    "http://localhost:9666",
    "http://192.168.30.50:9666",
    "http://192.168.30.50:5173",
    "http://192.168.30.50",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add GZip middleware for compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

DB_PATH = "backend/data/cipibot.db"

conversations = {}
db_result = get_db_all_connection(DB_PATH)


def add_conversation(user_number: str, bot_number: str) -> None:
    """create new conversation object"""
    conversations.update({user_number: Conversation(user_number, bot_number)})
    result = get_db_connection(
        user_number=user_number, bot_number=bot_number, db_name=DB_PATH
    )
    if not result:
        new_db_connection(
            user_number=user_number,
            bot_number=bot_number,
            result=conversations[user_number].get_params(),
            db_name=DB_PATH,
        )


for i in db_result:
    add_conversation(i[0], i[1])
for i in db_result:
    try:
        conversations[i[0]].put_params(i[2])
    except:
        print(f"{Style.BRIGHT}error restoring conv no: {i[0]}{Style.RESET_ALL}")

whatsapp_web_url = "http://localhost:8000/send"  # Replace with your endpoint URL
nest_asyncio.apply()

if sys.version_info < (3, 10):
    print("Tak bisa jalan di python < 3.10")
    sys.exit()


async def notify_admin(message: str) -> None:
    for i in cfg["CONFIG"]["ADMIN_NUMBER"]:
        admin_result = send_to_phone(i, cfg["CONFIG"]["BOT_NUMBER"], message)
        print(admin_result)
    return None


def generate_filename() -> str:
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(10))


def send_to_phone(user_number: str, bot_number: str, message: str):
    """send langsung ke WA, tapi ke *user_number*, bukan ke bot_number"""
    message = {
        "message": message,  # Replace with your message text
        "from": bot_number,  # Replace with the sender number
        "to": user_number,  # Replace with out bot number
    }  # type: ignore

    response = requests.post(whatsapp_web_url, json=message)

    if response.status_code == 200:
        return "Message sent successfully!"
    else:
        return f"Error sending message. Status code: {response.status_code}"


def send_to_agent_zero(
    message: str,
    context_id: Optional[str] = None,
    lifetime_hours: int = 24,
    project: Optional[str] = None,
    attachments: Optional[list] = None
) -> dict:
    """Kirim pesan ke Agent Zero API dan terima respons."""
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": AGENT_ZERO_API_KEY
    }
    
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
            AGENT_ZERO_URL,
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.ok:
            return {
                "success": True,
                "response": response.json().get("response", ""),
                "context_id": response.json().get("context_id")
            }
        else:
            error_data = response.json() if response.content else {}
            return {
                "success": False,
                "error": error_data.get("error", f"HTTP {response.status_code}")
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Gagal terhubung ke Agent Zero. Pastikan server berjalan."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def reformat_phone(text: str) -> str:
    """Ambil hanya nomor telfon saja, tanpa ending @c.us"""
    return "user" + str(text.split("@")[0])


def save_log(user_number: str) -> None:
    """cari object di conversations dict lalu save jadi log file"""
    if user_number not in conversations:
        return print(f"Conversation dengan {user_number} tidak ada")
    dir = cfg["CONFIG"]["LOGDIR"]
    filepath = str(user_number) + ".log"

    # Create the log directory if it doesn't exist
    if not os.path.exists(dir):
        os.makedirs(dir)

    # Write to the log file
    try:
        with open(dir + filepath, "a") as f:
            for i in conversations[user_number].messages:
                f.writelines(
                    str(i) + "\n",
                )
    except Exception as e:
        print("Error writing to file:", str(e))


def return_brb() -> str:
    alasan = [
        "ada tamu.",
        "angkat jemuran.",
        "karet kendor.",
        "kasih makan kucing",
        "ada tamu dateng.",
        "atep bolong.",
        "ada kebocoran.",
        "ada radiasi radioaktif.",
    ]
    message = "*BRB* - be right back, " + random.choice(alasan)
    return message


# Fungsi untuk memulai menjalankan setiap coroutine pada setiap objek
async def start_coroutines() -> None:
    coroutines = [obj.start_coroutine() for obj in conversations.values()]
    await asyncio.gather(*coroutines)


# Jalankan coroutines di background menggunakan event loop
async def start_background_tasks() -> None:
    loop = asyncio.get_running_loop()
    tasks = [loop.create_task(start_coroutines())]
    await asyncio.gather(*tasks)


# Admin authentication middleware
async def verify_admin_key(admin_key: str = Query(...)):
    print(f"DEBUG: Admin key received: '{admin_key}'")
    print(f"DEBUG: Admin numbers in config: {cfg['CONFIG']['ADMIN_NUMBER']}")

    if admin_key not in cfg["CONFIG"]["ADMIN_NUMBER"]:
        print(f"DEBUG: Admin key NOT in list. Returning 403 error.")
        raise HTTPException(status_code=403, detail="Admin access required")

    print(f"DEBUG: Admin key validated successfully!")
    return admin_key


# Admin API endpoints
@app.get("/api/admin/dashboard/stats")
async def get_dashboard_stats(
    admin_key: str = Depends(verify_admin_key),
) -> Dict[str, Any]:
    try:
        total_messages = 0
        total_tokens = 0

        for conv in conversations.values():
            total_messages += len(conv.messages)
            if hasattr(conv, "gpt_token_used"):
                total_tokens += conv.gpt_token_used

        return {
            "active_conversations": len(conversations),
            "maintenance_mode": msgprocess.on_maintenance,
            "server_status": "online",
            "total_messages": total_messages,
            "token_usage": total_tokens,
            "error_count": 0,  # TODO: Implement error tracking
            "uptime": 0,  # TODO: Implement uptime tracking
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get dashboard stats: {str(e)}"
        )


@app.get("/api/admin/conversations")
async def get_admin_conversations(
    search: Optional[str] = None,
    limit: int = 100,
    admin_key: str = Depends(verify_admin_key),
) -> List[Dict[str, Any]]:
    try:
        conv_data = []
        for user_number, conv_obj in conversations.items():
            persona_val = (
                conv_obj.persona.name
                if hasattr(conv_obj.persona, "name")
                else str(conv_obj.persona)
            )
            convmode_val = (
                conv_obj.convmode.name
                if hasattr(conv_obj.convmode, "name")
                else str(conv_obj.convmode)
            )
            convtype_val = (
                conv_obj.convtype.name
                if hasattr(conv_obj.convtype, "name")
                else str(conv_obj.convtype)
            )
            data = {
                "user_number": user_number,
                "user_name": conv_obj.user_name or "Unknown",
                "bot_name": conv_obj.bot_name or "Maya",
                "persona": persona_val.split(".")[-1]
                if "." in persona_val
                else persona_val,
                "convmode": convmode_val.split(".")[-1]
                if "." in convmode_val
                else convmode_val,
                "convtype": convtype_val.split(".")[-1]
                if "." in convtype_val
                else convtype_val,
                "last_active": getattr(conv_obj, "last_active", None),
            }

            if (
                not search
                or search.lower() in user_number.lower()
                or search.lower() in conv_obj.user_name.lower()
            ):
                conv_data.append(data)

        return conv_data[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get conversations: {str(e)}"
        )


@app.post("/api/admin/bulk/persona")
async def bulk_set_persona(
    request_data: Dict[str, Any], admin_key: str = Depends(verify_admin_key)
):
    try:
        user_numbers = request_data.get("user_numbers", [])
        persona_name = request_data.get("persona")

        if not user_numbers or not persona_name:
            raise HTTPException(
                status_code=400, detail="Missing user_numbers or persona"
            )

        # Convert persona name to enum
        try:
            persona = Persona[persona_name]
        except KeyError:
            raise HTTPException(
                status_code=400, detail=f"Invalid persona: {persona_name}"
            )

        success_count = 0
        for user_number in user_numbers:
            if user_number in conversations:
                pf.set_persona(persona, conversations[user_number])
                success_count += 1

        return {"message": f"Set {persona_name} for {success_count} conversations"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk operation failed: {str(e)}")


@app.post("/api/admin/bulk/convmode")
async def bulk_set_convmode(
    request_data: Dict[str, Any], admin_key: str = Depends(verify_admin_key)
):
    try:
        user_numbers = request_data.get("user_numbers", [])
        convmode_name = request_data.get("convmode")

        if not user_numbers or not convmode_name:
            raise HTTPException(
                status_code=400, detail="Missing user_numbers or convmode"
            )

        # Convert convmode name to enum
        try:
            convmode = ConvMode[convmode_name]
        except KeyError:
            raise HTTPException(
                status_code=400, detail=f"Invalid convmode: {convmode_name}"
            )

        success_count = 0
        for user_number in user_numbers:
            if user_number in conversations:
                conversations[user_number].set_convmode(convmode)
                success_count += 1

        return {"message": f"Set {convmode_name} for {success_count} conversations"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk operation failed: {str(e)}")


@app.post("/api/admin/bulk/convtype")
async def bulk_set_convtype(
    request_data: Dict[str, Any], admin_key: str = Depends(verify_admin_key)
):
    try:
        user_numbers = request_data.get("user_numbers", [])
        convtype_name = request_data.get("convtype")

        if not user_numbers or not convtype_name:
            raise HTTPException(
                status_code=400, detail="Missing user_numbers or convtype"
            )

        # Convert convtype name to enum
        try:
            convtype = ConvType[convtype_name]
        except KeyError:
            raise HTTPException(
                status_code=400, detail=f"Invalid convtype: {convtype_name}"
            )

        success_count = 0
        for user_number in user_numbers:
            if user_number in conversations:
                conversations[user_number].set_convtype(convtype)
                success_count += 1

        return {"message": f"Set {convtype_name} for {success_count} conversations"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk operation failed: {str(e)}")


# SQL Conversation table endpoints
@app.get("/api/admin/sql/conversations")
async def get_sql_conversations(
    limit: int = 100, offset: int = 0, admin_key: str = Depends(verify_admin_key)
) -> Dict[str, Any]:
    try:
        messages = get_all_conversations_sql(limit=limit, offset=offset)
        total = get_conversation_count()
        return {
            "messages": [
                {
                    "id": row[0],
                    "user_number": row[1],
                    "bot_number": row[2],
                    "timestamp": row[3],
                    "content": row[4],
                }
                for row in messages
            ],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get SQL conversations: {str(e)}"
        )


@app.get("/api/admin/sql/conversations/{user_number}")
async def get_sql_conversation_by_user(
    user_number: str,
    limit: int = 100,
    offset: int = 0,
    admin_key: str = Depends(verify_admin_key),
) -> Dict[str, Any]:
    try:
        # Get messages where user_number matches OR bot_number matches (all conversation)
        conn = sqlite3.connect(cfg['CONFIG']['DB_FILE'])
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM CONVERSATION WHERE user_number = ? OR bot_number = ? ORDER BY id DESC LIMIT ? OFFSET ?",
            (user_number, user_number, limit, offset),
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return {
            "messages": [
                {
                    "id": row[0],
                    "user_number": row[1],
                    "bot_number": row[2],
                    "timestamp": row[3],
                    "content": row[4],
                    "direction": "incoming" if row[1] == user_number else "outgoing"
                }
                for row in rows
            ],
            "user_number": user_number,
            "limit": limit,
            "offset": offset,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get SQL conversation: {str(e)}"
        )


# WebSocket for real-time updates
@app.websocket("/api/admin/ws")
async def websocket_endpoint(websocket: WebSocket, admin_key: str = Query(...)):
    await websocket.accept()

    # Verify admin key
    if admin_key not in cfg["CONFIG"]["ADMIN_NUMBER"]:
        await websocket.close(code=1008, reason="Invalid admin key")
        return

    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # Handle client messages if needed
                await websocket.send_json(
                    {
                        "type": "echo",
                        "message": f"Received: {message}",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            except json.JSONDecodeError:
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": "Invalid JSON",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
    except WebSocketDisconnect:
        print(f"Admin WebSocket disconnected: {admin_key}")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.close()


# Broadcast function for real-time updates (to be called from other functions)
async def broadcast_to_admins(message_type: str, data: Any):
    """Broadcast message to all connected admin WebSockets"""
    # This would need a connection manager implementation
    # For now, just print the message
    print(f"Broadcast to admins: {message_type} - {data}")


@app.put("/set_bot_name/{user_number}/{bot_name}")
async def set_bot_name(user_number: str, bot_name: str) -> Union[dict, dict, None]:
    if user_number not in conversations:
        return {"message": "user dont exist"}
    try:
        conversations[user_number].set_bot_name(bot_name)
    except Exception as e:
        return {"message": e}
    return {"message": "done"}


KOS_KEYWORDS = ["kos", "azana", "kamar", "kost", " sewa ", "penginapan", "hostel", "inn"]

async def _handle_message(request: Request, *, kos_routing: bool, group_prefix_required: bool, bot_config_key: str = "BOT_NUMBER"):
    """Shared handler untuk /messages dan /special_messages"""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    text = data.get("text", "")
    user_number = data.get("user_number", "")
    
    # Get bot_number from config based on endpoint
    bot_numbers = cfg["CONFIG"].get(bot_config_key, cfg["CONFIG"]["BOT_NUMBER"])
    bot_number = bot_numbers[0] if isinstance(bot_numbers, list) else bot_numbers

    # Filter: broadcast, newsletter
    if user_number.endswith("@broadcast") or user_number.endswith("@newsletter"):
        return

    # Filter: admin to bot message
    if not group_prefix_required and user_number in cfg["CONFIG"]["BOT_NUMBER"] and bot_number in cfg["CONFIG"]["ADMIN_NUMBER"]:
        return

    # Filter: group messages (unless special_messages)
    if not group_prefix_required and user_number.endswith("@g.us"):
        return

    # Filter: ignored users
    if user_number in cfg.get("IGNORE", {}).get("IGNORE", []):
        print(f"{Fore.WHITE}{Back.RED}IGNORED USER: {user_number}{Fore.RESET}{Back.RESET}")
        return

    # Check maintenance mode
    if msgprocess.on_maintenance:
        admin_numbers = cfg["CONFIG"]["ADMIN_NUMBER"]
        if user_number not in admin_numbers:
            print(f"{Fore.RED}{Back.WHITE}ON MAINTENANCE - Ignoring message from {user_number}{Fore.WHITE}{Back.BLACK}")
            return

    timestamp = data.get("timestamp", 0)
    notifyName = data.get("notifyName", "")
    msg_type = data.get("type", "chat")
    client = data.get("client", "whatsapp")
    author = data.get("author", "")
    hasMedia = data.get("hasMedia", False)
    message_dict = data.get("message", {})

    if not user_number or not text:
        return

    # Group prefix validation (for special_messages)
    if group_prefix_required and user_number.endswith("@g.us"):
        if user_number not in conversations:
            add_conversation(user_number=user_number, bot_number=bot_number)
        bot_name = conversations[user_number].bot_name.lower()
        if not text.lower().startswith(bot_name):
            return

    is_new_user = user_number not in conversations

    if is_new_user:
        add_conversation(user_number=user_number, bot_number=bot_number)

    print(f"📥 Received: user={user_number}, text={text[:50]}...")

    conversation_obj = conversations[user_number]
    
    # Update bot_number from config (in case it changed)
    conversation_obj.bot_number = bot_number
    
    if notifyName:
        conversation_obj.user_name = notifyName

    # KOS routing for new users
    if kos_routing:
        text_lower = text.lower()
        has_kos_keyword = any(kw in text_lower for kw in KOS_KEYWORDS)
        if is_new_user and not has_kos_keyword:
            print(f"📪 New user tanpa KOS keyword - ignored")
            return
        if is_new_user and has_kos_keyword:
            print(f"🎯 New user dengan keyword kos - set persona ke KOS_CS")
            pf.set_persona(Persona.KOS_CS, conversation_obj)
            cf.add_system(conversation_obj, cfg['KOS_CS']['M_S'])
            cf.add_role_user(conversation_obj, cfg['KOS_CS']['M_U'])
            cf.add_role_assistant(conversation_obj, cfg['KOS_CS']['M_A'])

    # Insert human message to DB
    human_say = "HUMAN: " + text
    dbo_insert_conv(user_number, bot_number, int(timestamp), human_say, DB_PATH)

    msg_obj = Message(
        text=text,
        user_number=user_number,
        bot_number=bot_number,
        timestamp=timestamp,
        notifyName=notifyName,
        type=msg_type,
        client=client,
        author=author,
        hasMedia=hasMedia,
        message=message_dict
    )

    try:
        response_text = await msgprocess.process(conversation_obj, message=msg_obj)
        if response_text is None:
            return {"message": ""}
    except Exception as err:
        print(
            f"{Fore.RED}{Back.WHITE}>>>>>>>>>>>>>>>> ERROR : "
            + f"{str(err)} <<<<<<<<<<<<<<<<<<<<<{Fore.WHITE}{Back.BLACK}"
        )
        try:
            await notify_admin(f"Ada error {str(err)} nih! dari {user_number}")
        except:
            pass
        conversation_obj.anti_flood = []
        return {"message": return_brb()}

    update_db_connection(
        user_number=user_number,
        bot_number=bot_number,
        result=conversation_obj.get_params(),
        db_name=DB_PATH,
    )

    return {"message": str(response_text)}


@app.post("/messages")
async def receive_message(request: Request):
    """Endpoint menerima pesan dari WhatsApp (index.js) - uses BOT_NUMBER"""
    return await _handle_message(request, kos_routing=True, group_prefix_required=False, bot_config_key="BOT_NUMBER")


@app.post("/special_messages")
async def receive_special_message(request: Request):
    """Endpoint alternatif - @g.us harus +bot_name prefix - uses BOT2_NUMBER"""
    return await _handle_message(request, kos_routing=False, group_prefix_required=True, bot_config_key="BOT2_NUMBER")


@app.get("/print_messages/{user_number}")
async def print_messages(user_number: str) -> str:  # type: ignore
    """Keluarkan log percakapan dengan nomor tertentu"""
    if user_number in conversations:
        return {"messages": str(conversations[user_number].messages)}  # type: ignore
    else:
        logging.error(f"save_log error finding user_number: {str(user_number)}")


@app.get("/save_logs")
async def save_logs() -> dict[str, str] | None:
    """save semua logs conversation ke dalam file log"""
    for i in conversations.keys():
        try:
            save_log(i)
            return {"save": "done"}
        except:
            logging.error("Error saving logs")


@app.post("/set_content")
async def set_content(message_content: MessageContent) -> dict[str, str]:
    "Inject conversation ke dalam object Conversation"
    roles = {
        "SYSTEM": "add_system",
        "USER": "add_role_user",
        "ASSISTANT": "add_role_assistant",
    }
    content = message_content.message

    if message_content.user_number not in conversations:
        add_conversation(message_content.user_number, message_content.bot_number)

    # getattr(conversations[message_content.user_number], roles[message_content.role] )(content)
    if message_content.role == "SYSTEM":
        cf.add_system(conversations[message_content.user_number], content)
        return {"message": "success setting system message"}
    if message_content.role == "USER":
        cf.add_role_user(conversations[message_content.user_number], content)
        return {"message": "success setting user message"}
    if message_content.role == "ASSISTANT":
        cf.add_role_assistant(conversations[message_content.user_number], content)
        return {"message": "success setting assistant message"}
    logging.debug(
        f"Inject:{message_content.role}:{content} to {message_content.user_number}"
    )

    return {"message": "Error setting content"}


@app.put("/create_conv/{user_number}/{bot_number}")
async def create_conv(user_number: str, bot_number: str) -> dict[str, str]:
    if user_number not in conversations:
        add_conversation(user_number, bot_number)
        return {"message": "done creation"}
    return {"message": "already exist"}


@app.put("/botquestion/{user_number}")
async def put_botquestion(
    user_number: str, botquestion: List[BotQuestion]
) -> dict[str, str]:
    # Menambahkan data yang diterima ke dalam list

    if user_number not in conversations:
        conv_obj = conversations.update(
            {user_number: Conversation(user_number, cfg["CONFIG"]["BOT_NUMBER"])}
        )

    conv_obj = conversations[user_number]
    conv_obj.botquestions.extend(botquestion)
    return {"message": "Data berhasil ditambahkan!"}


@app.put("/set_convmode/{user_number}/{convmode}")
async def set_mode(user_number: str, convmode: str) -> dict[str, str]:
    if user_number not in conversations:
        return {"detail": "user dont exist"}
    conv = conversations[user_number]
    try:
        convmode_enum = ConvMode[convmode.upper()]
        conv.set_convmode(convmode_enum)
    except Exception as e:
        return {"detail": f"error: {e}"}
    
    # Save to database - delete and re-insert
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CONNECTION WHERE user_number = ? AND bot_number = ?", 
                       (conv.user_number, conv.bot_number))
        conn.commit()
        cursor.execute("INSERT INTO CONNECTION (user_number, bot_number, value) VALUES (?, ?, ?)",
                       (conv.user_number, conv.bot_number, conv.get_params()))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        return {"detail": f"error saving: {e}"}
    
    return {"detail": f"set to {convmode}"}


@app.get("/botq/{user_number}")
async def get_botq(user_number: str) -> dict[str, str]:
    return {"message": str(conversations[user_number].botquestions)}


@app.get("/getmode/{user_number}")
async def getmode(user_number: str) -> dict[str, str]:
    return {"message": str(conversations[user_number].mode)}


@app.get("/run_question/{user_number}/{id}")
async def run_question(user_number: str, id: int = 1) -> dict[str, str]:
    if user_number not in conversations:
        return {"message": "user not exist"}
    conv = conversations[user_number]
    send_to_phone(
        user_number, cfg["CONFIG"]["BOT_NUMBER"], conv.botquestions[id].question
    )
    return {"message": "done"}


@app.get("/start_question/{user_number}")
async def start_question(user_number: str) -> dict[str, str]:
    if user_number not in conversations:
        return {"message": "user not exist"}
    conv = conversations[user_number]
    conv.mode = ConvMode.ASK
    send_to_phone(user_number, cfg["CONFIG"]["BOT_NUMBER"], conv.intro_msg)
    send_to_phone(
        user_number, cfg["CONFIG"]["BOT_NUMBER"], conv.botquestions[0].question
    )
    conv.question_asked = conv.botquestions[0].question
    return {"message": "done"}


@app.get("/reset_botquestions/{user_number}")
async def reset_botquestion(user_number: str) -> dict[str, str]:
    if user_number not in conversations:
        return {"detail": "user dont exist"}
    conversations[user_number].reset_botquestions()
    return {"message": "reset done"}


@app.get("/reset_channel/{user_number}")
async def reset_channel(user_number: str) -> dict[str, str]:
    if user_number not in conversations:
        return {"detail": "user dont exist"}
    pf.set_persona(Persona.ASSISTANT, conversations[user_number])
    pf.set_personality(
        "Maya",
        "ASSISTANT",
        "Hai, Aku Maya, aku akan berusaha membantumu",
        conversations[user_number],
    )
    conversations[user_number].anti_flood = []
    return {"message": "reset done"}


# Endpoint untuk merubah interval pada objek tertentu
@app.put("/set_interval/{user_number}/{interval}")
async def change_interval(user_number: str, interval: int) -> dict[str, str]:
    if user_number not in conversations:
        return {"message": "user does not exist"}
    conversations[user_number].set_interval(interval)
    return {"message": f"sudah di set menjadi {interval}"}


# Endpoint untuk memulai menjalankan method pada setiap objek
@app.get("/call_method")
async def start_method_call() -> dict[str, str]:
    await start_background_tasks()
    return {"message": "Method dijalankan pada setiap objek."}


@app.get("/botquestions/{user_number}")
async def botquestions(user_number: str) -> dict[str, str]:
    """check seluruh tanya-jawab di object conversation milik user"""
    if user_number not in conversations:
        return {"message": "user not found"}

    result = ""
    for id, item in enumerate(conversations[user_number].botquestions):
        result = result + f"{item.question}:{item.answer}\n"
    return {"message": result}


@app.put("/set_persona/{user_number}/{persona}")
async def set_persona(user_number: str, persona: str) -> dict[str, str]:
    if user_number not in conversations:
        return {"message": "user not found"}
    
    conv = conversations[user_number]
    old_params = conv.get_params()
    
    try:
        persona_enum = Persona[persona.upper()]
        pf.set_persona(persona_enum, conv)
    except Exception as e:
        print(f"ERROR in pf.set_persona: {e}")
        return {"message": f"error setting persona: {e}"}
    
    # Save to database - force update by deleting first then inserting
    try:
        # Delete old record and insert new
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CONNECTION WHERE user_number = ? AND bot_number = ?", 
                       (conv.user_number, conv.bot_number))
        conn.commit()
        cursor.execute("INSERT INTO CONNECTION (user_number, bot_number, value) VALUES (?, ?, ?)",
                       (conv.user_number, conv.bot_number, conv.get_params()))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"DEBUG: Saved persona={persona} for user={user_number}, bot={conv.bot_number}")
    except Exception as e:
        print(f"ERROR saving to DB: {e}")
        return {"message": f"error saving to DB: {e}"}
    
    return {"message": f"set to {persona}"}


@app.get("/obj_info/{user_number}")
async def obj_info(user_number: str) -> Union[dict, dict, None]:
    """Return the object in all conversation"""
    if user_number not in conversations:
        return {"message": "user does not exist"}
    result = conversations[user_number].get_params()
    return {"message": result}


@app.put("/set_interview/{user_number}")
async def set_interview(user_number: str, data: dict) -> dict[str, str]:
    if user_number not in conversations:
        return {"message": "user does not exist"}
    conversations[user_number].set_intro_msg(data["intro_msg"])
    conversations[user_number].set_outro_msg(data["outro_msg"])
    return {"mesage": "done set intro and outro"}


@app.get("/test_send/{user_number}")
async def test_send(user_number: str) -> dict:
    if user_number not in conversations:
        return {"message": "user does not exist"}
    response = conversations[user_number].send_msg("Hello")
    if response:
        return {"message": "Message sent"}
    else:
        return {"message": "error sending test"}


@app.post("/messages/media")
async def test_media_media() -> dict:
    """Test endpoint - returns text + image/pdf from media/ directory"""
    text = "Ini pesan dengan lampiran!"

    attachments = []

    jpg_att = encode_relative("test.jpg", "image/jpeg", "test.jpg")
    if jpg_att:
        attachments.append(jpg_att)

    pdf_att = encode_relative("test.pdf", "application/pdf", "test.pdf")
    if pdf_att:
        attachments.append(pdf_att)

    if attachments:
        return make_media_response(text, attachments)
    else:
        return {"message": text + " (no media files found)"}


@app.post("/api/test_media/{user_number}")
async def test_media(user_number: str, message: Optional[Message] = None) -> dict:
    """Test endpoint - returns text + image/pdf from media/ directory"""
    text = "Ini pesan dengan lampiran!"

    attachments = []

    jpg_att = encode_relative("test.jpg", "image/jpeg", "test.jpg")
    if jpg_att:
        attachments.append(jpg_att)

    pdf_att = encode_relative("test.pdf", "application/pdf", "test.pdf")
    if pdf_att:
        attachments.append(pdf_att)

    if attachments:
        return make_media_response(text, attachments)
    else:
        return {"message": text + " (no media files found)"}


@app.post("/agentzero")
async def agentzero_endpoint(request: Request) -> dict:
    """
    Relay endpoint - WhatsApp -> Server -> Agent Zero -> Server -> WhatsApp
    
    Request body:
    {
        "text": "Halo, ada yang bisa dibantu?",
        "user_number": "6285775300227@c.us",
        "bot_number": "6281234567890@c.us",
        "timestamp": 1700000000,
        "context_id": "ctx_abc123",  (optional)
        "project": "my-project",       (optional)
        "lifetime_hours": 24          (optional)
    }
    
    Response format (compatible with handleWaResponse in index.js):
    {
        "message": "{\"text\": \"Response text\", \"attachments\": [...]}"
    }
    """
    try:
        data = await request.json()
    except Exception as e:
        print(f"❌ Invalid JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    
    user_number = data.get("user_number")
    bot_number = data.get("bot_number")
    message_text = data.get("text") or data.get("message")
    context_id = data.get("context_id")
    project = data.get("project")
    lifetime_hours = data.get("lifetime_hours", 24)
    
    print(f"📥 Received: user={user_number}, text={str(message_text)[:50]}...")
    
    if not user_number or not bot_number or not message_text:
        print(f"❌ Missing fields: user={user_number}, bot={bot_number}, text={message_text}")
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: user_number, bot_number, text/message"
        )
    
    print(f"📤 Mengirim ke Agent Zero: user={user_number}, message={str(message_text)[:50]}...")
    
    result = send_to_agent_zero(
        message=message_text,
        context_id=context_id,
        lifetime_hours=lifetime_hours,
        project=project
    )
    
    if result["success"]:
        response_text = result["response"]
        new_context_id = result.get("context_id")
        
        print(f"✅ Respons dari Agent Zero: {str(response_text)[:100]}...")
        
        wa_response = {
            "text": response_text,
            "context_id": new_context_id
        }
        
        return {"message": json.dumps(wa_response)}
    else:
        error_message = f"Error Agent Zero: {result['error']}"
        print(f"❌ {error_message}")
        
        wa_response = {
            "text": error_message
        }
        
        return {"message": json.dumps(wa_response)}


@app.get("/ping")
async def ping() -> dict[str, str]:
    return {"message": "pong"}


@app.get("/api/admin/debug")
async def debug_admin(admin_key: str = Query(...)):
    """Debug endpoint to test admin authentication"""
    admin_numbers = cfg["CONFIG"]["ADMIN_NUMBER"]
    return {
        "received_key": admin_key,
        "valid_keys": admin_numbers,
        "is_valid": admin_key in admin_numbers,
        "config_file": "config.toml",
    }


@app.get("/list_conversations")
async def list_conversations() -> dict:
    list_conv = []
    all_conv = list(conversations.keys())
    print(all_conv)
    for i in all_conv:
        item = f"{conversations[i].user_number}###{conversations[i].user_name}"
        list_conv.append(item)
    return {"message": list_conv}


@app.get("/run_background_task/{user_number}")
async def run_background_task(user_number: str):
    if user_number not in conversations:
        return {"message": "user not found"}
    asyncio.create_task(conversations[user_number].start_coroutine())
    return {"message": "started"}


@app.get("/set_maintenance")
async def set_maintenance() -> dict:
    if msgprocess.on_maintenance:
        msgprocess.on_maintenance = False
        print(
            f"{Fore.RED}{Back.WHITE}MAINTENANCE FINISHED NOW!! - BACK TO NORMAL{Fore.WHITE}{Back.BLACK}"
        )
    else:
        msgprocess.on_maintenance = True
        print(
            f"{Fore.RED}{Back.WHITE}GO TO MAINTENANCE MODE NOW!!{Fore.WHITE}{Back.BLACK}"
        )
    return {"message": "Done setting"}


@app.get("/rebuild_connection_db")
async def rebuild_connection_db():
    for i in conversations.keys():
        update_db_connection(
            conversations[i].user_number,
            conversations[i].bot_number,
            conversations[i].get_params(),
            DB_PATH,
        )
    return {"message": "update completed"}


@app.put("/set_convtype/{user_number}/{convtype}")
async def set_convtype(user_number: str, convtype: str) -> dict[str, str]:
    if user_number not in conversations:
        return {"detail": "user dont exist"}
    conv = conversations[user_number]
    try:
        convtype_enum = ConvType[convtype.upper()]
        conv.set_convtype(convtype_enum)
    except Exception as e:
        return {"detail": f"error: {e}"}
    
    # Save to database - delete and re-insert
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CONNECTION WHERE user_number = ? AND bot_number = ?", 
                       (conv.user_number, conv.bot_number))
        conn.commit()
        cursor.execute("INSERT INTO CONNECTION (user_number, bot_number, value) VALUES (?, ?, ?)",
                       (conv.user_number, conv.bot_number, conv.get_params()))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        return {"detail": f"error saving: {e}"}
    
    return {"detail": f"{user_number} set to {convtype}"}


async def background_task():
    count = 0
    while True:
        count += 1
        # print("ping", count)
        await asyncio.sleep(10)


async def background_task2():
    count = 0
    while True:
        count += 1
        # print("pong", count)
        await asyncio.sleep(9)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_task())
    asyncio.create_task(background_task2())
    # asyncio.create_task(conversations[cfg['CONFIG']['ADMIN_NUMBER'][0]].start_coroutine())
    asyncio.create_task(msgprocess.process_queue_gpt())
    asyncio.create_task(msgprocess.process_queue_ooba())


# @app.on_event("shutdown")
# async def shutdown_event():
#     asyncio.current_task

# subprocess.run(["python", "startup_script.py"])

# Mount static files for Vue.js admin interface
if os.path.exists("static"):
    # Mount Vue.js SPA at root
    app.mount("/static", StaticFiles(directory="static", html=True), name="static")

    # SPA catch-all route - must be LAST
    @app.get("/{path:path}")
    async def serve_spa(path: str):
        """Serve Vue.js SPA for all non-API routes"""
        # Skip API routes
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")

        # Check if it's a static file
        static_path = os.path.join("static", path)
        if os.path.isfile(static_path):
            from fastapi.responses import FileResponse

            return FileResponse(static_path)

        # Serve index.html for SPA routes
        index_path = os.path.join("static", "index.html")
        if os.path.exists(index_path):
            from fastapi.responses import FileResponse

            return FileResponse(index_path)

        raise HTTPException(status_code=404, detail="Not found")
else:
    print("Warning: static directory not found. Admin interface will not be available.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8998)
