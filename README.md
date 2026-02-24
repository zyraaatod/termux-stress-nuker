# 🔥 Termux Stress Nuker

> ⚠️ **Disclaimer**: Tool ini hanya untuk testing dan educational purposes. Penggunaan tanpa izin adalah ILEGAL!

![Python](https://img.shields.io/badge/Python-3.7+-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Termux-orange?style=flat-square)

---

## 📋 Daftar Isi
- [Tentang](#tentang)
- [Persyaratan](#persyaratan)
- [Instalasi](#instalasi)
- [Penggunaan](#penggunaan)
- [Fitur](#fitur)
- [Warning](#⚠️-warning)

---

## 📖 Tentang

**Termux Stress Nuker** adalah tool stress testing yang dirancang untuk melakukan load testing pada website menggunakan Python dan async programming. Tool ini menggunakan multiple requests secara concurrent untuk testing purposes.

### 🎯 Use Case
- Testing performa website Anda sendiri
- Load testing infrastructure
- Security testing dengan izin pemilik

---

## ⚙️ Persyaratan

| Komponen | Versi |
|----------|-------|
| Python | 3.7+ |
| Termux | Latest |
| OS | Android |

### Dependencies
- `aiohttp` - HTTP client library
- `dnspython` - DNS query library

---

## 🚀 Instalasi

### Step 1: Update Termux
```bash
pkg update && pkg upgrade -y
```

### Step 2: Install Python & Git
```bash
pkg install python git -y
```

### Step 3: Clone Repository
```bash
git clone https://github.com/zyraaatod/termux-stress-nuker.git
cd termux-stress-nuker
```

### Step 4: Install Python Dependencies
```bash
pip install aiohttp dnspython
```

---

## 💻 Penggunaan

### Basic Usage
```bash
python3 stress_nuker.py https://target-website.com
```

### Advanced Usage
```bash
python3 stress_nuker.py https://target-website.com --threads 100 --duration 60
```

### Parameter Options
| Parameter | Deskripsi | Default |
|-----------|-----------|---------|
| `target` | URL target website | Required |
| `--threads` | Jumlah concurrent requests | 50 |
| `--duration` | Durasi testing (detik) | 30 |
| `--timeout` | Timeout per request (detik) | 10 |

---

## ✨ Fitur

✅ Async request processing untuk performance maksimal  
✅ Multiple concurrent connections  
✅ Real-time statistics & reporting  
✅ Custom headers support  
✅ Proxy support  
✅ User-friendly CLI interface  

---

## 📊 Contoh Output

```
[+] Starting Stress Test...
[+] Target: https://example.com
[+] Threads: 50
[+] Duration: 30 seconds

[*] Requests Sent: 5,234
[*] Success Rate: 95.2%
[*] Average Response Time: 245ms
[*] Peak Requests/sec: 174

[✓] Test Completed Successfully!
```

---

## ⚠️ Warning

🚨 **PENTING!** 

Sebelum menggunakan tool ini, pastikan:
- ✔️ Anda memiliki **izin tertulis** dari pemilik website/server
- ✔️ Testing dilakukan di **environment testing** yang telah disetujui
- ✔️ Anda memahami **konsekuensi hukum** dari testing tanpa izin
- ✔️ Anda mematuhi **undang-undang cyber crime** di negara Anda

**Penggunaan tanpa izin adalah ILEGAL dan dapat mengakibatkan tuntutan hukum! ⚖️**

---

## 🛠️ Troubleshooting

### Error: "ModuleNotFoundError: No module named 'aiohttp'"
```bash
pip install --upgrade pip
pip install aiohttp dnspython
```

### Error: "Connection refused"
- Pastikan target website accessible
- Check internet connection Anda
- Verify firewall settings

### Performa Lambat
- Kurangi jumlah threads
- Increase timeout value
- Check bandwidth/connection

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---


## 📞 Kontak & Support

- 📧 Email: [kudaterbang1441@gmail.com]
- 🐙 GitHub: [@zyraaatod](https://github.com/zyraaatod)
- 💬 Issues: [Report Bug](https://github.com/zyraaatod/termux-stress-nuker/issues)


**Last Updated**: 2026-02-24 06:26:49  
**Status**: ✅ Active & Maintained