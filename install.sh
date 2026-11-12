#!/data/data/com.termux/files/usr/bin/bash
set -e

CYAN='\033[96m'
GREEN='\033[92m'
RED='\033[91m'
RESET='\033[0m'

echo -e "${CYAN}MUX V2.6 - CYBER NEON INSTALLER${RESET}"

if ! command -v pkg >/dev/null 2>&1; then
    echo "This installer requires Termux."
    exit 1
fi

if [ ! -f "$(dirname "$0")/mux.py" ]; then
    echo -e "${RED}Error: mux.py not found!${RESET}"
    exit 1
fi

echo "[1/5] Updating packages..."
pkg update -y

echo "[2/5] Installing Python..."
pkg install -y python python-pip

echo "[3/5] Installing Requests..."
python -m pip install requests --break-system-packages

echo "[4/5] Installing MUX..."
mkdir -p "$HOME/.local/bin" "$HOME/.mux"

cp "$(dirname "$0")/mux.py" "$HOME/.local/bin/mux"
chmod +x "$HOME/.local/bin/mux"

if ! grep -qF 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc" 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi

if ! grep -qF 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.zshrc" 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
fi

echo "[5/5] Verifying..."
python -c "import requests"

export PATH="$HOME/.local/bin:$PATH"

echo -e "${GREEN}MUX V2.6 INSTALLED SUCCESSFULLY!${RESET}"
echo "Run: mux"
