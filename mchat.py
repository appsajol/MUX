
#!/usr/bin/env python3
"""
mChat V2.6 - Cyber Neon Edition
Global Group Chat for Termux
"""

import os
import sys
import json
import time
import sqlite3
import threading
import getpass
from datetime import datetime, timezone
from pathlib import Path

import requests


# =========================================================
# CONFIGURATION
# =========================================================

VERSION = "2.6"

APP_DIR = Path.home() / ".mchat"
APP_DIR.mkdir(parents=True, exist_ok=True)

DB_FILE = APP_DIR / "history.sqlite3"
CONFIG_FILE = APP_DIR / "config.json"

# Add your Firebase Web API key here.
# Do not publish your private credentials on GitHub.
API_KEY = os.environ.get(
    "MCHAT_FIREBASE_API_KEY",
    "AIzaSyDL2SOlI2KMMznshxRM2TWtGM4UVreQJWc"
)

DB_URL = (
    "https://project-cc66a079-4cfc-4fe5-b7a-"
    "default-rtdb.firebaseio.com"
)

AUTH_BASE = "https://identitytoolkit.googleapis.com/v1"
SECURE_TOKEN = "https://securetoken.googleapis.com/v1/token"

SESSION = requests.Session()

STOP = threading.Event()
seen = set()
state_lock = threading.Lock()


# =========================================================
# COLORS
# =========================================================

CYAN = "\033[96m"
GREEN = "\033[92m"
MAGENTA = "\033[95m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
WHITE = "\033[97m"
RESET = "\033[0m"
BOLD = "\033[1m"


# =========================================================
# BANNER
# =========================================================

def banner():
    os.system("clear")

    print(CYAN + BOLD + r"""
 __  __  _____ _   _    _  _____
|  \/  |/ ____| | | |  /\|_   _|
| \  / | |    | |_| | /  \ | |
| |\/| | |    |  _  |/ /\ \| |
| |  | | |____| | | / ____ \| |_
|_|  |_|\_____|_| |_/_/    \_\
""" + RESET)

    print(CYAN + BOLD + "                 mChat V2.6" + RESET)
    print(MAGENTA + "             CYBER NEON EDITION" + RESET)
    print(MAGENTA + "       GLOBAL GROUP CHAT • TERMUX" + RESET)
    print(CYAN + "-" * 54 + RESET)


# =========================================================
# DATABASE
# =========================================================

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
        """
        INSERT OR IGNORE INTO messages
        (id, username, body, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (mid, username, body, created)
    )

    con.commit()
    con.close()


def show_history():
    con = sqlite3.connect(DB_FILE)

    rows = con.execute(
        """
        SELECT username, body, created_at
        FROM messages
        ORDER BY created_at DESC
        LIMIT 30
        """
    ).fetchall()

    con.close()

    print(f"\n{MAGENTA}{BOLD}YOUR LOCAL HISTORY{RESET}")

    for name, body, created in reversed(rows):
        print(f"{CYAN}[{name}]{RESET} {body}")

    if not rows:
        print("No local messages yet.")


# =========================================================
# CONFIG FILE
# =========================================================

def load_config():
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            return {}

    return {}


def save_config(cfg):
    CONFIG_FILE.write_text(
        json.dumps(cfg, indent=2)
    )

    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass


# =========================================================
# FIREBASE AUTHENTICATION
# =========================================================

def check_api_key():
    if not API_KEY or API_KEY == "PASTE_YOUR_FIREBASE_API_KEY_HERE":
        raise RuntimeError(
            "Firebase API key missing. Add your Firebase Web API key "
            "to MCHAT_FIREBASE_API_KEY."
        )


def auth_request(endpoint, payload):
    check_api_key()

    response = SESSION.post(
        f"{AUTH_BASE}/{endpoint}?key={API_KEY}",
        json=payload,
        timeout=20
    )

    try:
        data = response.json()
    except ValueError:
        data = {}

    if not response.ok:
        message = data.get(
            "error", {}
        ).get("message", "Authentication failed")

        raise RuntimeError(message)

    return data


def refresh_session(cfg):
    if not cfg.get("refreshToken"):
        return False

    try:
        response = SESSION.post(
            f"{SECURE_TOKEN}?key={API_KEY}",
            data={
                "grant_type": "refresh_token",
                "refresh_token": cfg["refreshToken"]
            },
            timeout=20
        )

        data = response.json()

        if not response.ok:
            return False

        cfg["idToken"] = data["id_token"]
        cfg["refreshToken"] = data["refresh_token"]

        cfg["expiresAt"] = (
            time.time()
            + int(data.get("expires_in", 3600))
            - 60
        )

        save_config(cfg)
        return True

    except Exception:
        return False


def ensure_token(cfg):
    if (
        cfg.get("idToken")
        and time.time() < cfg.get("expiresAt", 0)
    ):
        return

    if not refresh_session(cfg):
        raise RuntimeError(
            "Login session expired. Please login again."
        )


def login_flow():
    cfg = load_config()

    username = (cfg.get("username") or "").strip()

    if not username:
        username = input(
            f"{CYAN}Choose your mChat username: {RESET}"
        ).strip()

    if not username or len(username) > 24:
        raise RuntimeError(
            "Username must be 1-24 characters."
        )

    print()
    print(f"{GREEN}[1]{RESET} Create Account")
    print(f"{GREEN}[2]{RESET} Login to Existing Account")

    choice = input(
        f"\n{YELLOW}Select 1 or 2: {RESET}"
    ).strip()

    email = input("Email: ").strip()
    password = getpass.getpass(
        "Password (minimum 6 characters): "
    )

    if len(password) < 6:
        raise RuntimeError(
            "Password must contain at least 6 characters."
        )

    if choice == "1":
        data = auth_request(
            "accounts:signUp",
            {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
        )

    elif choice == "2":
        data = auth_request(
            "accounts:signInWithPassword",
            {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
        )

    else:
        raise RuntimeError("Choose 1 or 2.")

    cfg.update({
        "username": username,
        "email": email,
        "uid": data["localId"],
        "idToken": data["idToken"],
        "refreshToken": data["refreshToken"],
        "expiresAt": (
            time.time()
            + int(data.get("expiresIn", 3600))
            - 60
        )
    })

    save_config(cfg)

    return cfg


# =========================================================
# FIREBASE DATABASE
# =========================================================

def db_request(method, path, cfg, **kwargs):
    check_api_key()
    ensure_token(cfg)

    params = kwargs.pop("params", {})
    params["auth"] = cfg["idToken"]

    url = (
        DB_URL.rstrip("/")
        + "/"
        + path.strip("/")
        + ".json"
    )

    response = SESSION.request(
        method,
        url,
        params=params,
        timeout=25,
        **kwargs
    )

    if response.status_code == 401:
        if refresh_session(cfg):
            params["auth"] = cfg["idToken"]

            response = SESSION.request(
                method,
                url,
                params=params,
                timeout=25,
                **kwargs
            )

    if not response.ok:
        try:
            detail = response.json()
        except Exception:
            detail = response.text

        raise RuntimeError(
            f"Database error ({response.status_code}): {detail}"
        )

    if not response.text:
        return None

    return response.json()


# =========================================================
# PRESENCE SYSTEM
# =========================================================

def timestamp():
    return datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")


def send_presence(cfg, status="online"):
    payload = {
        "username": cfg["username"],
        "status": status,
        "lastSeen": timestamp()
    }

    db_request(
        "PUT",
        f"presence/{cfg['uid']}",
        cfg,
        json=payload
    )


def heartbeat(cfg):
    while not STOP.wait(35):
        try:
            send_presence(cfg)
        except Exception as error:
            print(
                f"\n{YELLOW}[presence] {error}{RESET}"
            )


def list_members(cfg):
    data = db_request(
        "GET",
        "presence",
        cfg
    ) or {}

    now = time.time()
    online = []

    for item in data.values():
        if not isinstance(item, dict):
            continue

        try:
            last_seen = datetime.fromisoformat(
                item.get("lastSeen", "").replace(
                    "Z", "+00:00"
                )
            ).timestamp()

            if (
                item.get("status") == "online"
                and now - last_seen < 100
            ):
                online.append(
                    item.get("username", "Unknown")
                )

        except Exception:
            pass

    print(
        f"\n{GREEN}{BOLD}ONLINE MEMBERS "
        f"({len(online)}){RESET}"
    )

    for name in sorted(set(online), key=str.lower):
        print("  • " + name)

    if not online:
        print("  No active members detected.")


# =========================================================
# GLOBAL GROUP CHAT
# =========================================================

def fetch_messages(cfg):
    data = db_request(
        "GET",
        "groups/main/messages",
        cfg,
        params={
            "orderBy": '"$key"',
            "limitToLast": "40"
        }
    ) or {}

    if not isinstance(data, dict):
        return

    rows = []

    for mid, msg in data.items():
        if isinstance(msg, dict):
            rows.append((mid, msg))

    rows.sort(
        key=lambda item: item[1].get(
            "createdAt", ""
        )
    )

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

        print(
            f"\n{CYAN}[{msg.get('username', 'Unknown')}]{RESET} "
            f"{msg.get('text', '')}"
        )

        print(
            f"{YELLOW}mchat>{RESET} ",
            end="",
            flush=True
        )


def poller(cfg):
    while not STOP.wait(3):
        try:
            fetch_messages(cfg)

        except Exception as error:
            print(
                f"\n{RED}[reconnect] {error}{RESET}"
            )

            print(
                f"{YELLOW}mchat>{RESET} ",
                end="",
                flush=True
            )


def send_message(cfg, text):
    body = text[:1000]

    payload = {
        "username": cfg["username"],
        "uid": cfg["uid"],
        "text": body,
        "createdAt": timestamp()
    }

    result = db_request(
        "POST",
        "groups/main/messages",
        cfg,
        json=payload
    )

    if isinstance(result, dict) and result.get("name"):
        save_local(
            result["name"],
            cfg["username"],
            body,
            payload["createdAt"]
        )

        seen.add(result["name"])


# =========================================================
# CHAT SESSION
# =========================================================

def chat(cfg):
    init_db()
    STOP.clear()

    banner()

    print(
        f"{GREEN}Logged in as "
        f"{BOLD}{cfg['username']}{RESET}"
    )

    print(
        "Commands: /members  /history  /clear  /exit"
    )

    try:
        send_presence(cfg)
        fetch_messages(cfg)

    except Exception as error:
        print(
            f"\n{RED}Cannot connect: {error}{RESET}"
        )

        try:
            send_presence(cfg, "offline")
        except Exception:
            pass

        input("\nPress Enter to return to Main Menu...")
        return

    poll_thread = threading.Thread(
        target=poller,
        args=(cfg,),
        daemon=True
    )

    heartbeat_thread = threading.Thread(
        target=heartbeat,
        args=(cfg,),
        daemon=True
    )

    poll_thread.start()
    heartbeat_thread.start()

    try:
        while not STOP.is_set():

            try:
                line = input(
                    f"{YELLOW}mchat>{RESET} "
                ).strip()

            except (EOFError, KeyboardInterrupt):
                line = "/exit"

            if not line:
                continue

            if line == "/exit":
                break

            elif line == "/members":
                try:
                    list_members(cfg)
                except Exception as error:
                    print(
                        f"{RED}{error}{RESET}"
                    )

            elif line == "/history":
                show_history()

            elif line == "/clear":
                os.system("clear")
                banner()

            elif line.startswith("/"):
                print(
                    "Unknown command. Use "
                    "/members, /history, /clear, /exit."
                )

            else:
                try:
                    send_message(cfg, line)

                except Exception as error:
                    print(
                        f"{RED}Message not sent: {error}{RESET}"
                    )

    finally:
        STOP.set()

        try:
            send_presence(cfg, "offline")
        except Exception:
            pass

        poll_thread.join(timeout=4)
        heartbeat_thread.join(timeout=4)

        print(
            f"\n{GREEN}You are offline.{RESET}"
        )

        print(
            f"Local history saved in {DB_FILE}"
        )

        time.sleep(1)


# =========================================================
# USER PROFILE
# =========================================================

def show_profile():
    os.system("clear")
    banner()

    cfg = load_config()

    print(
        f"{MAGENTA}{BOLD}USER PROFILE{RESET}\n"
    )

    print(
        f"{CYAN}Username : {RESET}"
        f"{cfg.get('username', 'Not available')}"
    )

    print(
        f"{CYAN}Email    : {RESET}"
        f"{cfg.get('email', 'Not available')}"
    )

    print(
        f"{CYAN}User ID  : {RESET}"
        f"{cfg.get('uid', 'Not available')}"
    )

    print("\n" + "-" * 54)

    input("Press Enter to return to Main Menu...")


# =========================================================
# SETTINGS
# =========================================================

def show_settings():
    os.system("clear")
    banner()

    cfg = load_config()

    con = sqlite3.connect(DB_FILE)

    count = con.execute(
        "SELECT COUNT(*) FROM messages"
    ).fetchone()[0]

    con.close()

    print(
        f"{MAGENTA}{BOLD}SETTINGS{RESET}\n"
    )

    print(f"{CYAN}ACCOUNT INFORMATION{RESET}")

    print(
        f"Username       : "
        f"{cfg.get('username', 'Not available')}"
    )

    print(
        f"Email          : "
        f"{cfg.get('email', 'Not available')}"
    )

    print(f"\n{CYAN}LOCAL DATA{RESET}")

    print(f"Database       : {DB_FILE}")
    print(f"Saved Messages : {count}")
    print(f"Config File    : {CONFIG_FILE}")

    print("\n" + "-" * 54)

    input("Press Enter to return to Main Menu...")


# =========================================================
# ABOUT
# =========================================================

def show_about():
    os.system("clear")
    banner()

    print(
        f"{MAGENTA}{BOLD}ABOUT mChat{RESET}\n"
    )

    print(f"{CYAN}Application : {RESET}mChat")
    print(f"{CYAN}Version     : {RESET}{VERSION}")
    print(f"{CYAN}Edition     : {RESET}Cyber Neon")
    print(f"{CYAN}Platform    : {RESET}Termux / Android")
    print(f"{CYAN}Type        : {RESET}Global Group Chat")

    print(
        "\nA Python-based global group chat application."
    )

    print(
        "Powered by Firebase Authentication "
        "and Realtime Database."
    )

    print(
        "Local message history is stored using SQLite."
    )

    print("\n" + "-" * 54)

    input("Press Enter to return to Main Menu...")


# =========================================================
# MAIN MENU
# =========================================================

def main_menu():
    while True:
        os.system("clear")
        banner()

        print(
            f"{CYAN}{BOLD}MAIN MENU{RESET}\n"
        )

        print(f"{GREEN}[1]{RESET} Start Chat")
        print(f"{GREEN}[2]{RESET} User Profile")
        print(f"{GREEN}[3]{RESET} Settings")
        print(f"{GREEN}[4]{RESET} About mChat")
        print(f"{RED}[0]{RESET} Exit")

        print("\n" + "-" * 54)

        choice = input(
            f"{YELLOW}mChat Menu > {RESET}"
        ).strip()

        if choice == "1":
            try:
                print(
                    f"\n{CYAN}Starting mChat...{RESET}"
                )

                cfg = login_flow()
                chat(cfg)

            except KeyboardInterrupt:
                print(
                    f"\n{YELLOW}Login cancelled.{RESET}"
                )
                time.sleep(1)

            except Exception as error:
                print(
                    f"\n{RED}Error: {error}{RESET}"
                )

                input(
                    "\nPress Enter to return to Main Menu..."
                )

        elif choice == "2":
            show_profile()

        elif choice == "3":
            show_settings()

        elif choice == "4":
            show_about()

        elif choice == "0":
            cfg = load_config()

            if cfg.get("uid") and cfg.get("idToken"):
                try:
                    send_presence(cfg, "offline")
                except Exception:
                    pass

            STOP.set()

            print(
                f"\n{GREEN}mChat closed. You are offline.{RESET}"
            )

            break

        else:
            print(
                f"\n{RED}Invalid option!{RESET}"
            )

            time.sleep(1)


# =========================================================
# APPLICATION ENTRY POINT
# =========================================================

def main():
    try:
        init_db()
        main_menu()

    except KeyboardInterrupt:
        STOP.set()

        print(
            f"\n{GREEN}mChat closed.{RESET}"
        )

    except Exception as error:
        STOP.set()

        print(
            f"\n{RED}Fatal Error: {error}{RESET}"
        )


if __name__ == "__main__":
    main()

