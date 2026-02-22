import os
import time
import gc

# Mengimpor modul-modul yang sudah dipisah
from utils import clear_screen, load_config, save_config, go_to_home_screen, get_roblox_packages, launch_to_vip_server, clean_system_cache
from telemetry import deploy_telemetry_lua, get_instances_telemetry
from discord_bot import generate_log_text, send_discord_report

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
    loop_count = 0
    total_cleans = 0 

    while True:
        try:
            time.sleep(600) 
            loop_count += 1
            
            if loop_count >= 3:
                clean_system_cache()
                total_cleans += 1 
                loop_count = 0 
                
            instances_data = get_instances_telemetry(packages)
            log_text = generate_log_text(instances_data, total_cleans)
            
            clear_screen()
            print(log_text)
            print("\n[!] Mesin berjalan normal di latar belakang.")
            print("[!] Tekan CTRL+C dua kali dengan cepat untuk mematikan bot.")
            
            send_discord_report(config["webhook_url"], log_text)
            
            del instances_data
            del log_text
            gc.collect()
            
        except KeyboardInterrupt:
            print("\n[!] Peringatan: Input terdeteksi. Skrip menahan diri...")
            time.sleep(2)
        except Exception:
            pass

def main():
    config = load_config()
    
    while True:
        clear_screen()
        print("====================================")
        print("        ARSY V2.0 PURE AFK          ")
        print("====================================")
        print("[1] Jalankan")
        print("[2] Link Private server")
        print("[3] Link Discord")
        print("[0] Keluar")
        print("====================================")
        
        print(f"\n* VIP Link: {'[Terisi]' if config['vip_link'] else '[KOSONG]'}")
        print(f"* Discord:  {'[Terisi]' if config['webhook_url'] else '[KOSONG]'}")
        
        choice = input("\nPilih Menu (0-3): ")
        
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
        elif choice == '0':
            clear_screen()
            break
        else:
            print("Pilihan tidak valid.")
            time.sleep(1)

if __name__ == "__main__":
    main()
