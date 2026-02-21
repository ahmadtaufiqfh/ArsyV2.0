# 🍃 Arsy v2.0 - Pure AFK Engine

Arsy v2.0 adalah mesin *auto-farming* Roblox super ringan yang dirancang khusus untuk berjalan 24/7 di emulator Android/Termux (seperti Redfinger). Mengorbankan antarmuka UI demi **penghematan RAM maksimum**, skrip ini bekerja secara senyap sebagai *Daemon* (Layanan Latar Belakang).

## 🚀 Fitur Utama (Zero-UI Architecture)
* **Ghost-Touch Immunity:** Tidak ada input yang diterima setelah mesin berjalan, kebal terhadap sentuhan layar yang tidak disengaja.
* **Auto-Hide Termux:** Otomatis menyembunyikan layar terminal dan kembali ke *Home Screen* Android sesaat setelah dieksekusi.
* **Smart Garbage Collector:** Rutin mengeksekusi `am kill-all` dan `drop_caches` setiap 30 menit tanpa mengganggu atau menutup game Roblox.
* **Heartbeat Telemetry (Lua):** Skrip Lua yang sangat ringan mengirimkan "detak jantung" (waktu lokal) ke memori perangkat setiap 30 detik untuk mendeteksi *Disconnect* atau *Crash* secara presisi.
* **Discord Auto-Reporter:** Merekam jejak pemakaian RAM, siklus pembersihan, dan status akun, lalu mengirimkannya ke Discord dalam format log profesional.

## 🛠️ Persyaratan Sistem
* Termux dengan akses **Root** (`su`).
* Python terinstal (`pkg install python -y`).
* Aplikasi Roblox (Mendukung *multi-clone*).

## ⚡ Cara Penggunaan
1. Lakukan *clone repository* ini di Termux Anda:
   ```bash
   git clone [https://github.com/UsernameAnda/arsyv2.git](https://github.com/UsernameAnda/arsyv2.git)
   cd arsyv2
