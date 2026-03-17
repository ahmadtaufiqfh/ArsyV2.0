import os
import time
import gc
import sys
import subprocess

from utils import clear_screen, load_config, save_config, go_to_home_screen, get_roblox_packages, launch_to_vip_server, clean_system_cache, apply_grid_layout
from telemetry import deploy_telemetry_lua, get_instances_telemetry
from discord_bot import generate_log_text, send_discord_report

# ==========================================
# OPTIMASI 1: PENGHAPUS RAM TERMUX & ANTI STAIRCASE
# ==========================================
def deep_clear_termux():
    # Ini akan mereset format TTY Termux 100% aman
    sys.stdout.write('\033c\033[3J')
    sys.stdout.flush()

# ==========================================
# OPTIMASI 2: PEMBERSIH RAM KERNEL ANDROID
# ==========================================
def drop_android_ram():
    try:
        subprocess.run(["su", "-c", "sync; echo 3 > /proc/sys/vm/drop_caches"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def run_engine(config):
    packages = get_roblox_packages()
    
    if not packages:
        print("\n[❌] Tidak ada aplikasi Roblox yang terinstal!")
        time.sleep(2)
        return

    go_to_home_screen()
    
    for pkg in packages:
        subprocess.run(["su", "-c", f"am force-stop {pkg}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    deploy_telemetry_lua(packages)
    time.sleep(2)
    
    launch_to_vip_server(packages, config["vip_link"])
    
    gc.collect() 
    drop_android_ram()
    
    print("\n[+] Menunggu 45 detik agar Roblox memuat game sepenuhnya...")
    time.sleep(45)

    loop_count = 0
    total_cleans = 0 

    while True:
        try:
            instances_data = get_instances_telemetry(packages)
            log_text = generate_log_text(instances_data, total_cleans)
            
            deep_clear_termux()
            print("====================================")
            print("        ARSY V2.0 LIVE MONITOR      ")
            print("====================================\n")
            print(log_text)
            print("\n[!] Mesin stabil berjalan di latar belakang.")
            print("[!] Laporan Discord di-update setiap 30 detik.")
            print("[!] Tekan CTRL+C dua kali dengan cepat untuk mematikan bot.")
            
            try:
                send_discord_report(config["webhook_url"], log_text)
            except Exception as e:
                print(f"\n[!] Info: Gagal sinkronisasi ke Discord ({e})")
            
            del instances_data
            del log_text
            gc.collect()
            
            time.sleep(30) 
            
            loop_count += 1
            if loop_count >= 20:
                clean_system_cache()  
                drop_android_ram()    
                total_cleans += 1 
                loop_count = 0 
                
        except KeyboardInterrupt:
            print("\n[!] Peringatan: Input terdeteksi. Skrip menahan diri...")
            time.sleep(2)
        except Exception as e:
            print(f"\n[!] Error fatal pada mesin utama: {e}")
            time.sleep(5) 

def main():
    config = load_config()
    
    while True:
        deep_clear_termux()
        print("====================================")
        print("        ARSY V2.0 PURE AFK          ")
        print("====================================")
        print("[1] Jalankan")
        print("[2] Link Private server")
        print("[3] Link Discord")
        print("[4] Atur Layout Grid")
        print("[0] Keluar")
        print("====================================")
        
        print(f"\n* VIP Link: {'[Terisi]' if config['vip_link'] else '[KOSONG]'}")
        print(f"* Discord:  {'[Terisi]' if config['webhook_url'] else '[KOSONG]'}")
        
        choice = input("\nPilih Menu (0-4): ")
        
        if choice == '1':
            if not config['vip_link'] or not config['webhook_url']:
                print("\n[!] Peringatan: Anda harus mengisi Link VIP dan Discord!")
                time.sleep(2)
            else:
                run_engine(config)
                break 
        elif choice == '2':
            print(f"\nLink lama: {config['vip_link']}")
            new_vip = input("Masukkan Link VIP baru: ")
            if new_vip.strip():
                config['vip_link'] = new_vip.strip()
                save_config(config)
                print("[+] Disimpan!")
                time.sleep(1)
        elif choice == '3':
            print(f"\nLink lama: {config['webhook_url']}")
            new_web = input("Masukkan Webhook baru: ")
            if new_web.strip():
                config['webhook_url'] = new_web.strip()
                save_config(config)
                print("[+] Disimpan!")
                time.sleep(1)
                
        # ==========================================
        # OPSI 4: EKSEKUSI GRID LAYOUT 
        # ==========================================
        elif choice == '4':
            packages = get_roblox_packages()
            if not packages:
                print("\n[!] Tidak ada aplikasi Roblox yang terinstal!")
                time.sleep(2)
            else:
                print(f"\n[+] Memulai Setup Grid Layout untuk {len(packages)} aplikasi...")
                print("[+] Mohon tunggu, sedang menyuntikkan koordinat & membuka aplikasi...")
                
                # Eksekusi Grid Layout (Sudah kebal Freeze)
                apply_grid_layout(packages)
                
                print("\n[+] Semua aplikasi telah terbuka dengan layout presisi.")
                print("[+] Menunggu 5 detik untuk konfirmasi visual di layar...")
                time.sleep(5)
                
                print("\n[+] Menutup kembali seluruh aplikasi Roblox...")
                for pkg in packages:
                    # Menutup secara aman menggunakan subprocess
                    subprocess.run(["su", "-c", f"am force-stop {pkg}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                print("[+] Selesai! Mengembalikan ke menu utama...")
                time.sleep(2)

        elif choice == '0':
            deep_clear_termux()
            break
        else:
            print("Pilihan tidak valid.")
            time.sleep(1)

if __name__ == "__main__":
    main()
