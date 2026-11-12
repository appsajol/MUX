#!/usr/bin/env python3
"""MUX V2.6 - Cyber Neon"""
import json, os, sys, time, sqlite3, threading, getpass
from datetime import datetime, timezone
from pathlib import Path
import requests

VERSION = "2.6"
APP_DIR = Path.home() / ".mux"
APP_DIR.mkdir(exist_ok=True)
DB_FILE = APP_DIR / "history.sqlite3"
CONFIG_FILE = APP_DIR / "config.json"

API_KEY = "AIzaSyDL2SOlI2KMMznshxRM2TWtGM4UVreQJWc"
DB_URL = "https://project-cc66a079-4cfc-4fe5-b7a-default-rtdb.firebaseio.com"
AUTH_BASE = "https://identitytoolkit.googleapis.com/v1"
SECURE_TOKEN = "https://securetoken.googleapis.com/v1/token"

SESSION = requests.Session()
STOP = threading.Event()
seen = set()

RESET = "\033[0m"
BOLD = "\033[1m"

THEMES = {
    "1": {"name": "Cyber Neon", "cyan": "\033[96m", "green": "\033[92m",
          "magenta": "\033[95m", "yellow": "\033[93m", "red": "\033[91m"},
    "2": {"name": "Matrix", "cyan": "\033[92m", "green": "\033[92m",
          "magenta": "\033[32m", "yellow": "\033[93m", "red": "\033[91m"},
    "3": {"name": "Red Alert", "cyan": "\033[91m", "green": "\033[91m",
          "magenta": "\033[31m", "yellow": "\033[93m", "red": "\033[91m"},
    "4": {"name": "Purple Neon", "cyan": "\033[95m", "green": "\033[95m",
          "magenta": "\033[35m", "yellow": "\033[93m", "red": "\033[91m"},
}

CFG = {}


def colors():
    theme = THEMES.get(CFG.get("theme", "1"), THEMES["1"])
    return theme


def c(name):
    return colors()[name]


def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass


def banner():
    os.system("clear")
    header = CFG.get("header", "MUX V2.6 - CYBER NEON")
    print(c("cyan") + BOLD + r"""
 __  __ _   _ __  __
|  \/  | | | |  \/  |
| |\/| | | | | |\/| |
| |  | | |_| | |  | |
|_|  |_|\__, |_|  |_|
         __/ |
        |___/
""" + RESET)
    print(c("magenta") + BOLD + "  " + header + RESET)
    print(c("green") + "  GLOBAL GROUP CHAT • TERMUX EDITION" + RESET)
    print(c("cyan") + "-" * 48 + RESET)


def main_menu():
    while True:
        banner()
        print(c("cyan") + BOLD + "             MAIN MENU" + RESET)
        print()
        print(f" {c('green')}[1]{RESET} Start MUX")
        print(f" {c('green')}[2]{RESET} Header Settings")
        print(f" {c('green')}[3]{RESET} Change Theme")
        print(f" {c('green')}[4]{RESET} User Profile")
        print(f" {c('green')}[5]{RESET} Settings")
        print(f" {c('green')}[6]{RESET} About MUX")
        print(f" {c('magenta')}{BOLD}[7] 💬 NEW CHAT MENU{RESET}")
        print(f" {c('red')}[0]{RESET} Exit")
        print()
        choice = input(c("yellow") + "MUX > " + RESET).strip()

        if choice in ("1", "7"):
            start_chat()
        elif choice == "2":
            header_settings()
        elif choice == "3":
            theme_settings()
        elif choice == "4":
            profile()
        elif choice == "5":
            settings()
        elif choice == "6":
            about()
        elif choice == "0":
            print(c("green") + "Goodbye! MUX offline." + RESET)
            break
        else:
            input("Invalid option. Press Enter...")


def header_settings():
    while True:
        banner()
        print(c("cyan") + BOLD + "HEADER SETTINGS" + RESET)
        print("1. Cyber Neon Header")
        print("2. Matrix Header")
        print("3. Red Alert Header")
        print("4. Purple Neon Header")
        print("5. Custom Header")
        print("6. Reset Header")
        print("0. Back")
        choice = input("\nSelect: ").strip()

        presets = {
            "1": "MUX V2.6 - CYBER NEON",
            "2": "MUX V2.6 - MATRIX",
            "3": "MUX V2.6 - RED ALERT",
            "4": "MUX V2.6 - PURPLE NEON",
        }

        if choice in presets:
            CFG["header"] = presets[choice]
            save_config(CFG)
            print(c("green") + "Header updated!" + RESET)
        elif choice == "5":
            value = input("Enter your custom header (max 40 characters): ").strip()
            if value and len(value) <= 40:
                CFG["header"] = value
                save_config(CFG)
                print(c("green") + "Custom header saved!" + RESET)
            else:
                print(c("red") + "Invalid header." + RESET)
        elif choice == "6":
            CFG["header"] = "MUX V2.6 - CYBER NEON"
            save_config(CFG)
            print(c("green") + "Default header restored!" + RESET)
        elif choice == "0":
            return
        else:
            print("Invalid option.")

        input("\nPress Enter to continue...")


def theme_settings():
    banner()
    print(c("cyan") + BOLD + "THEME SETTINGS" + RESET)
    for key, theme in THEMES.items():
        print(f"{key}. {theme['name']}")
    print("0. Back")

    choice = input("\nChoose theme: ").strip()
    if choice in THEMES:
        CFG["theme"] = choice
        save_config(CFG)
        print(c("green") + f"{THEMES[choice]['name']} theme activated!" + RESET)
    elif choice != "0":
        print("Invalid theme.")

    input("\nPress Enter to continue...")


def profile():
    banner()
    print(c("cyan") + BOLD + "USER PROFILE" + RESET)
    print("Username :", CFG.get("username", "Not set"))
    print("Email    :", CFG.get("email", "Not set"))
    print("User ID  :", CFG.get("uid", "Not logged in"))
    print("Version  :", VERSION)
    input("\nPress Enter to return...")


def settings():
    while True:
        banner()
        print(c("cyan") + BOLD + "SETTINGS" + RESET)
        print("1. View saved account")
        print("2. Clear local chat history")
        print("3. Back")

        choice = input("\nSelect: ").strip()
        if choice == "1":
            print("Username:", CFG.get("username", "Not set"))
            print("Email:", CFG.get("email", "Not set"))
            input("\nPress Enter...")
        elif choice == "2":
            confirm = input("Delete all local chat history? (yes/no): ").strip().lower()
            if confirm == "yes":
                con = sqlite3.connect(DB_FILE)
                con.execute("DELETE FROM messages")
                con.commit()
                con.close()
                print(c("green") + "Local history cleared." + RESET)
            input("\nPress Enter...")
        elif choice == "3":
            return
        else:
            print("Invalid option.")


def about():
    banner()
    print(c("cyan") + BOLD + "ABOUT MUX" + RESET)
    print("Name       : MUX")
    print("Version    : 2.6")
    print("Edition    : Cyber Neon")
    print("Platform   : Termux / Android")
    print("Chat       : Firebase Realtime Database")
    print("History    : Local SQLite")
    print("Developer  : MUX Project")
    input("\nPress Enter to return...")


def init_db():
    con = sqlite3.connect(DB_FILE)
    con.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    con.commit()
    con.close()


def save_local(mid, username, body, created):
    con = sqlite3.connect(DB_FILE)
    con.execute(
        "INSERT OR IGNORE INTO messages(id,username,body,created_at) VALUES(?,?,?,?)",
        (mid, username, body, created)
    )
    con.commit()
    con.close()


def auth_request(endpoint, payload):
    r = SESSION.post(
        f"{AUTH_BASE}/{endpoint}?key={API_KEY}",
        json=payload,
        timeout=20
    )
    data = r.json()
    if not r.ok:
        msg = data.get("error", {}).get("message", "Authentication failed")
        raise RuntimeError(msg)
    return data


def refresh_session(cfg):
    if not cfg.get("refreshToken"):
        return False

    r = SESSION.post(
        f"{SECURE_TOKEN}?key={API_KEY}",
        data={
            "grant_type": "refresh_token",
            "refresh_token": cfg["refreshToken"]
        },
        timeout=20
    )
    data = r.json()

    if not r.ok:
        return False

    cfg["idToken"] = data["id_token"]
    cfg["refreshToken"] = data["refresh_token"]
    cfg["expiresAt"] = time.time() + int(data.get("expires_in", 3600)) - 60
    save_config(cfg)
    return True


def ensure_token(cfg):
    if cfg.get("idToken") and time.time() < cfg.get("expiresAt", 0):
        return
    if not refresh_session(cfg):
        raise RuntimeError("Login session expired. Please sign in again.")


def login_flow():
    cfg = load_config()
    username = (cfg.get("username") or "").strip()

    if not username:
        username = input(c("cyan") + "Choose your MUX username: " + RESET).strip()

    if not username or len(username) > 24:
        raise RuntimeError("Username must be 1–24 characters.")

    print("\n1) Create account")
    print("2) Login to existing account")
    choice = input("Select 1 or 2: ").strip()
    email = input("Email: ").strip()
    password = getpass.getpass("Password (minimum 6 characters): ")

    if choice == "1":
        data = auth_request("accounts:signUp", {
            "email": email,
            "password": password,
            "returnSecureToken": True
        })
    elif choice == "2":
        data = auth_request("accounts:signInWithPassword", {
            "email": email,
            "password": password,
            "returnSecureToken": True
        })
    else:
        raise RuntimeError("Choose 1 or 2.")

    cfg.update({
        "username": username,
        "email": email,
        "uid": data["localId"],
        "idToken": data["idToken"],
        "refreshToken": data["refreshToken"],
        "expiresAt": time.time() + int(data.get("expiresIn", 3600)) - 60
    })
    save_config(cfg)
    return cfg


def db_request(method, path, cfg, **kwargs):
    ensure_token(cfg)
    params = kwargs.pop("params", {})
    params["auth"] = cfg["idToken"]

    url = DB_URL.rstrip("/") + "/" + path.strip("/") + ".json"
    r = SESSION.request(method, url, params=params, timeout=25, **kwargs)

    if r.status_code == 401 and refresh_session(cfg):
        params["auth"] = cfg["idToken"]
        r = SESSION.request(method, url, params=params, timeout=25, **kwargs)

    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"Database error ({r.status_code}): {detail}")

    if not r.text:
        return None
    return r.json()


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def send_presence(cfg, status="online"):
    payload = {
        "username": cfg["username"],
        "status": status,
        "lastSeen": timestamp()
    }
    db_request("PUT", f"presence/{cfg['uid']}", cfg, json=payload)


def heartbeat(cfg):
    while not STOP.wait(35):
        try:
            send_presence(cfg)
        except Exception as e:
            print(f"\n{c('yellow')}[presence] {e}{RESET}")


def list_members(cfg):
    data = db_request("GET", "presence", cfg) or {}
    now = time.time()
    online = []

    for item in data.values():
        if not isinstance(item, dict):
            continue
        try:
            dt = datetime.fromisoformat(
                item.get("lastSeen", "").replace("Z", "+00:00")
            ).timestamp()
            if item.get("status") == "online" and now - dt < 100:
                online.append(item.get("username", "Unknown"))
        except Exception:
            pass

    print(f"\n{c('green')}ONLINE MEMBERS ({len(set(online))}){RESET}")
    for name in sorted(set(online), key=str.lower):
        print("  • " + name)
    if not online:
        print("  No active members detected.")


def fetch_messages(cfg):
    data = db_request(
        "GET",
        "groups/main/messages",
        cfg,
        params={"orderBy": '"$key"', "limitToLast": "40"}
    ) or {}

    if not isinstance(data, dict):
        return

    rows = []
    for mid, msg in data.items():
        if isinstance(msg, dict):
            rows.append((mid, msg))

    rows.sort(key=lambda x: x[1].get("createdAt", ""))

    for mid, msg in rows:
        if mid in seen:
            continue
        seen.add(mid)
        save_local(
            mid,
            msg.get("username", "Unknown"),
            msg.get("text", ""),
            msg.get("createdAt", "")
        )
        print(f"\n{c('cyan')}[{msg.get('username', 'Unknown')}]{RESET} "
              f"{msg.get('text', '')}")
        print(f"{c('yellow')}mux>{RESET} ", end="", flush=True)


def poller(cfg):
    while not STOP.wait(3):
        try:
            fetch_messages(cfg)
        except Exception as e:
            print(f"\n{c('red')}[reconnect] {e}{RESET}")
            print(f"{c('yellow')}mux>{RESET} ", end="", flush=True)


def send_message(cfg, text):
    payload = {
        "username": cfg["username"],
        "uid": cfg["uid"],
        "text": text[:1000],
        "createdAt": timestamp()
    }
    result = db_request(
        "POST",
        "groups/main/messages",
        cfg,
        json=payload
    )

    if isinstance(result, dict) and result.get("name"):
        save_local(result["name"], cfg["username"], text[:1000],
                   payload["createdAt"])
        seen.add(result["name"])


def show_history():
    con = sqlite3.connect(DB_FILE)
    rows = con.execute(
        "SELECT username,body,created_at FROM messages "
        "ORDER BY created_at DESC LIMIT 30"
    ).fetchall()
    con.close()

    print(f"\n{c('magenta')}YOUR LOCAL HISTORY (latest 30){RESET}")
    for name, body, created in reversed(rows):
        print(f"[{name}] {body}")
    if not rows:
        print("No local messages yet.")


def chat(cfg):
    init_db()
    STOP.clear()
    banner()

    print(f"{c('green')}Logged in as {BOLD}{cfg['username']}{RESET}")
    print("Commands: /members  /history  /clear  /help  /exit")

    try:
        send_presence(cfg)
        fetch_messages(cfg)
    except Exception as e:
        print(f"{c('red')}Cannot connect: {e}{RESET}")
        return

    threading.Thread(target=poller, args=(cfg,), daemon=True).start()
    threading.Thread(target=heartbeat, args=(cfg,), daemon=True).start()

    while not STOP.is_set():
        try:
            line = input(f"{c('yellow')}mux>{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            line = "/exit"

        if not line:
            continue

        if line == "/exit":
            break
        elif line == "/members":
            try:
                list_members(cfg)
            except Exception as e:
                print(f"{c('red')}{e}{RESET}")
        elif line == "/history":
            show_history()
        elif line == "/clear":
            os.system("clear")
            banner()
        elif line == "/help":
            print("Available commands:")
            print("/members  - Show online members")
            print("/history  - Show local chat history")
            print("/clear    - Clear terminal screen")
            print("/help     - Show commands")
            print("/exit     - Leave chat")
        elif line.startswith("/"):
            print("Unknown command. Type /help.")
        else:
            try:
                send_message(cfg, line)
            except Exception as e:
                print(f"{c('red')}Message not sent: {e}{RESET}")

    STOP.set()
    try:
        send_presence(cfg, "offline")
    except Exception:
        pass

    print(f"{c('green')}You are offline. Local history saved.{RESET}")


def start_chat():
    try:
        cfg = login_flow()
        chat(cfg)
    except requests.RequestException as e:
        print(f"{c('red')}Network error: {e}{RESET}")
        input("\nPress Enter to return to menu...")
    except Exception as e:
        print(f"{c('red')}MUX error: {e}{RESET}")
        input("\nPress Enter to return to menu...")


def main():
    global CFG
    init_db()
    CFG = load_config()
    main_menu()


if __name__ == "__main__":
    main()
