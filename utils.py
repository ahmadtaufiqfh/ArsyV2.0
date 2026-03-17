import os
import time
import gc
import sys

from utils import clear_screen, load_config, save_config, go_to_home_screen, get_roblox_packages, launch_to_vip_server, clean_system_cache, apply_grid_layout
from telemetry import deploy_telemetry_lua, get_instances_telemetry
from discord_bot import generate_log_text, send_discord_report

def deep_clear_termux():
    os.system("stty sane")
    os.system("clear")

def drop_android_ram():
    try:
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
    
    print("\n[+] Memulai peluncuran otomatis ke Server...")
    # Mengeksekusi peluncuran server dengan batas yang sudah diatur di Menu 2
    launch_to_vip_server(packages, config.get("vip_link", ""), config.get("vip_limit", 0), config.get("public_link", ""))
    
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
        print("[2] Pengaturan Link Server (VIP/Public)")
        print("[3] Link Discord")
        print("[4] Atur Layout Grid")
        print("[0] Keluar & Bersihkan")
        print("====================================")
        
        limit_text = "[Semua Akun]" if config.get("vip_limit", 0) == 0 else f"[{config.get('vip_limit')} Akun]"
        print(f"\n* Target VIP  : {limit_text}")
        print(f"* VIP Link    : {'[Terisi]' if config.get('vip_link') else '[KOSONG]'}")
        print(f"* Public Link : {'[Terisi]' if config.get('public_link') else '[KOSONG]'}")
        print(f"* Discord     : {'[Terisi]' if config.get('webhook_url') else '[KOSONG]'}")
        
        choice = input("\nPilih Menu (0-4): ")
        
        if choice == '1':
            if not config.get('webhook_url'):
                print("\n[!] Peringatan: Anda harus mengisi Link Discord!")
                time.sleep(2)
            elif not config.get('vip_link') and not config.get('public_link'):
                print("\n[!] Peringatan: Anda harus mengisi setidaknya satu Link (VIP atau Public) di Menu 2!")
                time.sleep(2)
            else:
                run_engine(config)
                break 
                
        # ==========================================
        # MENU 2: PENGATURAN LINK SPLIT (VIP & PUBLIC)
        # ==========================================
        elif choice == '2':
            print("\n=== PENGATURAN LINK SERVER ===")
            print("Ketik '0' jika ingin MENGHAPUS link, atau cukup tekan ENTER untuk melewati.")
            
            print(f"\n1. Link VIP Utama: {config.get('vip_link', 'KOSONG')}")
            new_vip = input("   Masukkan Link VIP baru: ").strip()
            if new_vip == '0':
                config['vip_link'] = ""
            elif new_vip:
                config['vip_link'] = new_vip

            print(f"\n2. Batas Akun VIP: {config.get('vip_limit', 0)}")
            print("   (Contoh: Jika diisi 4, maka 4 akun pertama masuk VIP. Ketik 0 agar SEMUA masuk VIP)")
            limit_input = input("   Berapa akun yang masuk VIP? : ").strip()
            if limit_input.isdigit():
                config['vip_limit'] = int(limit_input)

            print(f"\n3. Link Public / Sisa: {config.get('public_link', 'KOSONG')}")
            print("   (Link ini dipakai untuk sisa akun. Kosongkan jika ingin sisa akun hanya diam di menu Roblox)")
            new_pub = input("   Masukkan Link Public baru: ").strip()
            if new_pub == '0':
                config['public_link'] = ""
            elif new_pub:
                config['public_link'] = new_pub

            save_config(config)
            print("\n[+] Pengaturan Server Berhasil Disimpan!")
            time.sleep(2)
            
        elif choice == '3':
            print(f"\nLink lama: {config.get('webhook_url', '')}")
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
