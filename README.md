INSTALASI & PENGGUNAAN:

1. INSTALL DI TERMUX:
 
# Update package 
pkg update && pkg upgrade -y

# Install python dan dependencies
pkg install python -y

pkg install git -y

# Clone repository (simpan sebagai file terpisah)
git clone https://github.com/zyraaatod/termux-stress-nuker.git

cd termux-stress-nuker

# Install python packages
pip install aiohttp dnspython

# Jalankan tool
python3 stress_nuker.py https://target-website.com
