import os
import time
import gc
import sys

from utils import clear_screen, load_config, save_config, go_to_home_screen, get_roblox_packages, launch_to_vip_server, clean_system_cache, apply_grid_layout
from telemetry import deploy_telemetry_lua, get_instances_telemetry
from discord_bot import generate_log_text, send_discord_report

# ==========================================
# OPTIMASI 1: PENGHAPUS RAM TERMUX & ANTI MIRING (STTY SANE)
# ==========================================
def deep_clear_termux():
    os.system("stty sane")
    os.system("clear")

def drop_android_ram():
    try:
        # Ditambahkan > /dev/null 2>&1 agar jika dilarang sistem Cloud Phone, errornya disembunyikan
        os.system("su -c 'sync; echo 3 > /proc/sys/vm/drop_caches > /dev/null 2>&1'")
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
        os.system(f"su -c 'am force-stop {pkg}'")
    
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
    os.system("stty sane")
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
        print("[0] Keluar & Bersihkan")
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
                
        elif choice == '4':
            packages = get_roblox_packages()
            if not packages:
                print("\n[!] Tidak ada aplikasi Roblox yang terinstal!")
                time.sleep(2)
            else:
                print(f"\n[+] Memulai Setup Grid Layout untuk {len(packages)} aplikasi...")
                print("[+] Memerlukan waktu, mohon tunggu Android bekerja...")
                
                apply_grid_layout(packages)
                
                print("\n[+] Semua aplikasi telah terbuka!")
                print("[+] Menunggu 10 detik agar Anda bisa mengamati hasilnya di layar...")
                time.sleep(10)
                
                print("\n[+] Menutup kembali seluruh aplikasi Roblox...")
                for pkg in packages:
                    os.system(f"su -c 'am force-stop {pkg}'")
                
                print("[+] Selesai! Mengembalikan ke menu utama...")
                time.sleep(2)

        elif choice == '0':
            print("\n[+] Menutup semua aplikasi Roblox...")
            packages = get_roblox_packages()
            for pkg in packages:
                os.system(f"su -c 'am force-stop {pkg}'")
            
            print("[+] Mengosongkan Cache & RAM (Ini mungkin butuh 3 detik)...")
            drop_android_ram()
            time.sleep(1)
            
            print("\n[+] Perangkat Anda sudah bersih dan ringan! Selamat tinggal.")
            time.sleep(2)
            deep_clear_termux()
            break
        else:
            print("Pilihan tidak valid.")
            time.sleep(1)

if __name__ == "__main__":
    main()
