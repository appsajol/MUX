#!/usr/bin/env python3
"""MUX V2.6 - Cyber Neon global group chat for Termux."""
import json, os, sys, time, sqlite3, threading, getpass, signal
from datetime import datetime, timezone
from pathlib import Path
import requests

VERSION = '2.6'
APP_DIR = Path.home() / '.mux'
APP_DIR.mkdir(exist_ok=True)
DB_FILE = APP_DIR / 'history.sqlite3'
CONFIG_FILE = APP_DIR / 'config.json'
API_KEY = 'AIzaSyDL2SOlI2KMMznshxRM2TWtGM4UVreQJWc'
DB_URL = 'https://project-cc66a079-4cfc-4fe5-b7a-default-rtdb.firebaseio.com'
AUTH_BASE = 'https://identitytoolkit.googleapis.com/v1'
SECURE_TOKEN = 'https://securetoken.googleapis.com/v1/token'
SESSION = requests.Session()
STOP = threading.Event()
seen = set()
state_lock = threading.Lock()

CYAN='\033[96m'; GREEN='\033[92m'; MAGENTA='\033[95m'; YELLOW='\033[93m'; RED='\033[91m'; RESET='\033[0m'; BOLD='\033[1m'

def banner():
    os.system('clear')
    print(CYAN + BOLD + r''' __  __ _   _ __  __
|  \/  | | | |  \/  |
| |\/| | | | | |\/| |
| |  | | |_| | |  | |
|_|  |_|\__, |_|  |_|
         __/ |       V2.6
        |___/   CYBER NEON''' + RESET)
    print(MAGENTA + '  GLOBAL GROUP CHAT  •  TERMUX EDITION' + RESET)
    print('-' * 54)

def init_db():
    con=sqlite3.connect(DB_FILE)
    con.execute('CREATE TABLE IF NOT EXISTS messages (id TEXT PRIMARY KEY, username TEXT NOT NULL, body TEXT NOT NULL, created_at TEXT NOT NULL)')
    con.commit(); con.close()

def save_local(mid, username, body, created):
    con=sqlite3.connect(DB_FILE)
    con.execute('INSERT OR IGNORE INTO messages(id,username,body,created_at) VALUES(?,?,?,?)',(mid,username,body,created))
    con.commit(); con.close()

def load_config():
    if CONFIG_FILE.exists():
        try: return json.loads(CONFIG_FILE.read_text())
        except Exception: return {}
    return {}

def save_config(cfg):
    CONFIG_FILE.write_text(json.dumps(cfg,indent=2))
    try: os.chmod(CONFIG_FILE,0o600)
    except OSError: pass

def auth_request(endpoint, payload):
    r=SESSION.post(f'{AUTH_BASE}/{endpoint}?key={API_KEY}',json=payload,timeout=20)
    data=r.json()
    if not r.ok:
        msg=data.get('error',{}).get('message','Authentication failed')
        raise RuntimeError(msg)
    return data

def refresh_session(cfg):
    if not cfg.get('refreshToken'): return False
    r=SESSION.post(f'{SECURE_TOKEN}?key={API_KEY}',data={'grant_type':'refresh_token','refresh_token':cfg['refreshToken']},timeout=20)
    data=r.json()
    if not r.ok: return False
    cfg['idToken']=data['id_token']; cfg['refreshToken']=data['refresh_token']; cfg['expiresAt']=time.time()+int(data.get('expires_in',3600))-60
    save_config(cfg); return True

def ensure_token(cfg):
    if cfg.get('idToken') and time.time() < cfg.get('expiresAt',0): return
    if not refresh_session(cfg): raise RuntimeError('Login session expired. Please restart MUX and sign in again.')

def login_flow():
    cfg=load_config()
    username=(cfg.get('username') or '').strip()
    if not username:
        username=input(f'{CYAN}Choose your MUX username: {RESET}').strip()
    if not username or len(username)>24:
        raise RuntimeError('Username must be 1–24 characters.')
    print('\n1) Create account\n2) Login to existing account')
    choice=input('Select 1 or 2: ').strip()
    email=input('Email: ').strip()
    password=getpass.getpass('Password (minimum 6 characters): ')
    if choice=='1': data=auth_request('accounts:signUp',{'email':email,'password':password,'returnSecureToken':True})
    elif choice=='2': data=auth_request('accounts:signInWithPassword',{'email':email,'password':password,'returnSecureToken':True})
    else: raise RuntimeError('Choose 1 or 2.')
    cfg.update({'username':username,'email':email,'uid':data['localId'],'idToken':data['idToken'],'refreshToken':data['refreshToken'],'expiresAt':time.time()+int(data.get('expiresIn',3600))-60})
    save_config(cfg)
    return cfg

def db_request(method, path, cfg, **kwargs):
    ensure_token(cfg)
    params=kwargs.pop('params',{})
    params['auth']=cfg['idToken']
    url=DB_URL.rstrip('/') + '/' + path.strip('/') + '.json'
    r=SESSION.request(method,url,params=params,timeout=25,**kwargs)
    if r.status_code==401:
        if refresh_session(cfg):
            params['auth']=cfg['idToken']; r=SESSION.request(method,url,params=params,timeout=25,**kwargs)
    if not r.ok:
        try: detail=r.json()
        except Exception: detail=r.text
        raise RuntimeError(f'Database error ({r.status_code}): {detail}')
    if not r.text: return None
    return r.json()

def timestamp(): return datetime.now(timezone.utc).isoformat(timespec='seconds')

def send_presence(cfg, status='online'):
    payload={'username':cfg['username'],'status':status,'lastSeen':timestamp()}
    db_request('PUT',f"presence/{cfg['uid']}",cfg,json=payload)

def heartbeat(cfg):
    while not STOP.wait(35):
        try: send_presence(cfg)
        except Exception as e: print(f'\n{YELLOW}[presence] {e}{RESET}')

def list_members(cfg):
    data=db_request('GET','presence',cfg) or {}
    now=time.time(); online=[]
    for item in data.values():
        if not isinstance(item,dict): continue
        try:
            dt=datetime.fromisoformat(item.get('lastSeen','').replace('Z','+00:00')).timestamp()
            if item.get('status')=='online' and now-dt<100: online.append(item.get('username','Unknown'))
        except Exception: pass
    print(f'\n{GREEN}ONLINE MEMBERS ({len(online)}){RESET}')
    for name in sorted(set(online),key=str.lower): print('  • '+name)
    if not online: print('  No active members detected.')

def fetch_messages(cfg):
    data=db_request('GET','groups/main/messages',cfg,params={'orderBy':'"$key"','limitToLast':'40'}) or {}
    if not isinstance(data,dict): return
    rows=[]
    for mid,msg in data.items():
        if isinstance(msg,dict): rows.append((mid,msg))
    rows.sort(key=lambda x: x[1].get('createdAt',''))
    for mid,msg in rows:
        if mid in seen: continue
        seen.add(mid)
        save_local(mid,msg.get('username','Unknown'),msg.get('text',''),msg.get('createdAt',''))
        print(f"\n{CYAN}[{msg.get('username','Unknown')}]{RESET} {msg.get('text','')}")
        print(f'{YELLOW}mux>{RESET} ',end='',flush=True)

def poller(cfg):
    while not STOP.wait(3):
        try: fetch_messages(cfg)
        except Exception as e: print(f'\n{RED}[reconnect] {e}{RESET}\n{YELLOW}mux>{RESET} ',end='',flush=True)

def send_message(cfg, text):
    payload={'username':cfg['username'],'uid':cfg['uid'],'text':text[:1000],'createdAt':timestamp()}
    result=db_request('POST','groups/main/messages',cfg,json=payload)
    if isinstance(result,dict) and result.get('name'):
        save_local(result['name'],cfg['username'],text[:1000],payload['createdAt'])
        seen.add(result['name'])

def show_history():
    con=sqlite3.connect(DB_FILE)
    rows=con.execute('SELECT username,body,created_at FROM messages ORDER BY created_at DESC LIMIT 30').fetchall(); con.close()
    print(f'\n{MAGENTA}YOUR LOCAL HISTORY (latest 30){RESET}')
    for name,body,created in reversed(rows): print(f'[{name}] {body}')
    if not rows: print('No local messages yet.')

def chat(cfg):
    init_db(); banner()
    print(f'{GREEN}Logged in as {BOLD}{cfg["username"]}{RESET}')
    print('Commands: /members  /history  /clear  /exit')
    try:
        send_presence(cfg)
        fetch_messages(cfg)
    except Exception as e:
        print(f'{RED}Cannot connect: {e}{RESET}'); return
    threading.Thread(target=poller,args=(cfg,),daemon=True).start()
    threading.Thread(target=heartbeat,args=(cfg,),daemon=True).start()
    while not STOP.is_set():
        try: line=input(f'{YELLOW}mux>{RESET} ').strip()
        except (EOFError,KeyboardInterrupt): line='/exit'
        if not line: continue
        if line=='/exit': break
        if line=='/members':
            try: list_members(cfg)
            except Exception as e: print(f'{RED}{e}{RESET}')
        elif line=='/history': show_history()
        elif line=='/clear': os.system('clear'); banner()
        elif line.startswith('/'):
            print('Unknown command. Use /members, /history, /clear, /exit.')
        else:
            try: send_message(cfg,line)
            except Exception as e: print(f'{RED}Message not sent: {e}{RESET}')
    STOP.set()
    try: send_presence(cfg,'offline')
    except Exception: pass
    print(f'{GREEN}You are offline. Local history is saved in {DB_FILE}{RESET}')

def main():
    init_db()
    try:
        cfg=login_flow()
        chat(cfg)
    except requests.RequestException as e:
        print(f'{RED}Network error: {e}{RESET}')
        sys.exit(1)
    except Exception as e:
        print(f'{RED}MUX error: {e}{RESET}')
        sys.exit(1)

if __name__=='__main__': main()
