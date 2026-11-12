#!/data/data/com.termux/files/usr/bin/bash
set -e
CYAN='\033[96m'; GREEN='\033[92m'; RESET='\033[0m'
echo -e "${CYAN}MUX V2.6 – CYBER NEON INSTALLER${RESET}"
if ! command -v pkg >/dev/null 2>&1; then echo 'This installer must run inside Termux.'; exit 1; fi
pkg update -y
pkg install -y python
python -m pip install --upgrade pip
python -m pip install requests
mkdir -p "$HOME/.local/bin" "$HOME/.mux"
cp "$(dirname "$0")/mux.py" "$HOME/.local/bin/mux"
chmod +x "$HOME/.local/bin/mux"
if ! grep -q 'HOME/.local/bin' "$HOME/.bashrc" 2>/dev/null; then echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"; fi
if ! grep -q 'HOME/.local/bin' "$HOME/.zshrc" 2>/dev/null; then echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"; fi
echo -e "${GREEN}MUX V2.6 installed.${RESET}"
echo 'Run: source ~/.bashrc  (or reopen Termux), then type: mux'
