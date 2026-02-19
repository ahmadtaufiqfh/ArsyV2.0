#!/bin/bash
echo -e "\e[1;32m=== Memulai Instalasi Arsy V2.0 ===\e[0m"

# Update system & install kebutuhan (Mode Anti-Macet)
export DEBIAN_FRONTEND=noninteractive
pkg update -y
pkg upgrade -y -o Dpkg::Options::="--force-confold"
pkg install curl python tmux -y

# Membuat direktori kerja
echo -e "\e[1;34m[*] Mengunduh Core Engine...\e[0m"
mkdir -p ~/arsy_v2
cd ~/arsy_v2

# Mengunduh core.py dari repo baru Anda
curl -sL https://raw.githubusercontent.com/ahmadtaufiqfh/ArsyV2.0/main/core.py -o core.py

# Membuat file konfigurasi default (jika belum ada)
if [ ! -f arsy_config.json ]; then
    echo '{"ps_link": "", "apps": {}}' > arsy_config.json
fi

# Membuat Shortcut untuk Widget Termux
echo -e "\e[1;34m[*] Membuat Shortcut Widget...\e[0m"
mkdir -p ~/.shortcuts
echo '#!/bin/bash' > ~/.shortcuts/Start_Arsy
echo 'termux-wake-lock' >> ~/.shortcuts/Start_Arsy
echo 'tmux new-session -d -s arsy2 "cd ~/arsy_v2 && python core.py"' >> ~/.shortcuts/Start_Arsy
chmod +x ~/.shortcuts/Start_Arsy

echo -e "\e[1;32m[✓] Instalasi Selesai Sempurna!\e[0m"
echo -e "Silakan letakkan Termux:Widget di layar Home Redfinger Anda."
