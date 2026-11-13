
#!/data/data/com.termux/files/usr/bin/bash

set -e

APP_DIR="$HOME/.local/share/mchat"
BIN_DIR="$HOME/.local/bin"
SOURCE_DIR="$(cd "$(dirname "$0")" && pwd)"

echo ""
echo "=================================="
echo "       mChat V2.6 INSTALLER"
echo "          CYBER NEON"
echo "=================================="

if [ ! -f "$SOURCE_DIR/mchat.py" ]; then
    echo "ERROR: mchat.py was not found!"
    echo "Keep install.sh and mchat.py together."
    exit 1
fi

echo "[1/4] Installing requirements..."
pkg install python -y
python -m pip install requests

echo "[2/4] Installing mChat..."
mkdir -p "$APP_DIR" "$BIN_DIR"
cp "$SOURCE_DIR/mchat.py" "$APP_DIR/mchat.py"

echo "[3/4] Creating global command..."

cat > "$BIN_DIR/mchat" <<'LAUNCHER'
#!/data/data/com.termux/files/usr/bin/bash
APP_DIR="$HOME/.local/share/mchat"

if [ ! -f "$APP_DIR/mchat.py" ]; then
    echo "mChat is not installed. Run install.sh again."
    exit 1
fi

exec python "$APP_DIR/mchat.py" "$@"
LAUNCHER

chmod +x "$BIN_DIR/mchat"

echo "[4/4] Configuring PATH..."

PROFILE="$HOME/.bashrc"
touch "$PROFILE"

if ! grep -Fq 'export PATH="$HOME/.local/bin:$PATH"' "$PROFILE"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$PROFILE"
fi

export PATH="$BIN_DIR:$PATH"

echo ""
echo "=================================="
echo "     mChat INSTALLATION DONE!"
echo "=================================="
echo ""
echo "Run from anywhere:"
echo "mchat"
echo ""
echo "If command is not found, restart Termux"
echo "or run: source ~/.bashrc"
echo "=================================="
