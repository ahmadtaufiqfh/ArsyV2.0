import os
import time
import gc
import sys

from utils import clear_screen, load_config, save_config, go_to_home_screen, get_roblox_packages, launch_to_vip_server, clean_system_cache, apply_grid_layout
from telemetry import deploy_telemetry_lua, get_instances_telemetry
from discord_bot import generate_log_text, send_discord_report

def deep_clear_termux():
    sys.stdout.write('\033c')
    sys.stdout.flush()

def drop_android_ram():
    try:
        os.system("su -c 'sync; echo 3 > /proc/sys/vm/drop_caches' > /dev/null 2>&1")
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
        os.system(f"su -c 'am force-stop {pkg}' > /dev/null 2>&1")
    
    deploy_telemetry_lua(packages)
    time.sleep(2)
    
    print("\n[+] Memulai peluncuran otomatis ke Server...")
    vip_pkgs = config.get("vip_packages", packages)
    # Memasukkan link public ke fungsi peluncur
    launch_to_vip_server(packages, config.get("vip_link", ""), config.get("public_link", ""), vip_pkgs)
    
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
    # Pastikan bersih sekali saat awal
    deep_clear_termux()
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
        
        vip_pkgs = config.get("vip_packages", [])
        limit_text = f"[{len(vip_pkgs)} Akun VIP]" if vip_pkgs else "[Belum diset/Semua VIP]"
        
        print(f"\n* Jalur Server: {limit_text}")
        print(f"* VIP Link    : {'[Terisi]' if config.get('vip_link') else '[KOSONG]'}")
        print(f"* Public Link : {'[Terisi]' if config.get('public_link') else '[KOSONG]'}")
        print(f"* Discord     : {'[Terisi]' if config.get('webhook_url') else '[KOSONG]'}")
        
        try:
            choice = input("\nPilih Menu (0-4): ").strip()
        except EOFError:
            break
            
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
        # MENU 2: PENGATURAN AMAN ANTI-FREEZE
        # ==========================================
        elif choice == '2':
            print("\n=== PENGATURAN LINK SERVER ===")
            print("1. Link Private (VIP):", config.get('vip_link', 'KOSONG'))
            new_vip = input("   Masukkan Link (Ketik 0 untuk Hapus, ENTER lewati): ").strip()
            if new_vip == '0':
                config['vip_link'] = ""
            elif new_vip:
                config['vip_link'] = new_vip

            print("\n2. Link Public (Untuk sisa akun):", config.get('public_link', 'KOSONG'))
            print("   Catatan: Masukkan link game agar sisa akun ikut bermain di Public Server.")
            new_pub = input("   Masukkan Link (Ketik 0 untuk Hapus, ENTER lewati): ").strip()
            if new_pub == '0':
                config['public_link'] = ""
            elif new_pub:
                config['public_link'] = new_pub

            print("\n3. Pengaturan Jalur Aplikasi (VIP vs Public)")
            packages = get_roblox_packages() # <-- Tidak akan merusak TTY lagi
            current_vips = config.get("vip_packages", [])
            
            if not packages:
                print("   [!] Tidak ada aplikasi Roblox terdeteksi.")
            else:
                print("   Daftar Aplikasi Anda:")
                sorted_pkgs = sorted(packages)
                for i, pkg in enumerate(sorted_pkgs):
                    status = "[VIP]" if (pkg in current_vips or not current_vips) else "[Public]"
                    print(f"   {i+1}. {pkg} {status}")

                print("\n   -> Ketik NOMOR aplikasi yang ingin dimasukkan ke PRIVATE SERVER.")
                print("   -> Pisahkan dengan koma (Contoh: 1,2,3)")
                print("   -> Sisa nomor yang tidak diketik akan otomatis masuk PUBLIC SERVER.")
                print("   -> Kosongkan (tekan ENTER) jika tidak ingin mengubah data.")
                print("   -> Ketik '0' jika ingin SEMUA akun masuk PUBLIC.")
                
                ans = input("   Pilihan Anda: ").strip()
                if ans == '0':
                    config['vip_packages'] = []
                elif ans != '':
                    new_vips = []
                    parts = ans.split(',')
                    for p in parts:
                        if p.strip().isdigit():
                            idx = int(p.strip()) - 1
                            if 0 <= idx < len(sorted_pkgs):
                                new_vips.append(sorted_pkgs[idx])
                    if new_vips:
                        config['vip_packages'] = new_vips
                
            save_config(config)
            print("\n[+] Pengaturan Server Berhasil Disimpan!")
            time.sleep(2)
            
        elif choice == '3':
            print(f"\nLink lama: {config.get('webhook_url', '')}")
            new_web = input("Masukkan Webhook baru: ").strip()
            if new_web:
                config['webhook_url'] = new_web
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
                    os.system(f"su -c 'am force-stop {pkg}' > /dev/null 2>&1")
                
                print("[+] Selesai! Mengembalikan ke menu utama...")
                time.sleep(2)

        elif choice == '0':
            print("\n[+] Menutup semua aplikasi Roblox...")
            packages = get_roblox_packages()
            for pkg in packages:
                os.system(f"su -c 'am force-stop {pkg}' > /dev/null 2>&1")
            
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
