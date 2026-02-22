import os
import time
import subprocess

def deploy_telemetry_lua(packages):
    lua_script = """
repeat task.wait() until game:IsLoaded()
local Players = game:GetService("Players")

local usn = Players.LocalPlayer and Players.LocalPlayer.Name or "Unknown"
local startTime = os.time()

-- SILENT ANTI-AFK HOOK
pcall(function()
    for _, connection in pairs(getconnections(Players.LocalPlayer.Idled)) do
        connection:Disable()
    end
end)

-- CFRAME SHIFT (Bypass Custom Anti-AFK Game)
task.spawn(function()
    while task.wait(900) do
        pcall(function()
            local char = Players.LocalPlayer.Character
            if char and char:FindFirstChild("HumanoidRootPart") then
                local hrp = char.HumanoidRootPart
                hrp.CFrame = hrp.CFrame * CFrame.new(0, 0.1, 0) 
                task.wait(0.5)
                hrp.CFrame = hrp.CFrame * CFrame.new(0, -0.1, 0)
            end
        end)
    end
end)

-- HEARTBEAT
while task.wait(30) do
    pcall(function()
        writefile("arsy_status.txt", usn .. "|" .. tostring(os.time()) .. "|" .. tostring(startTime))
    end)
end
"""
    with open("temp_arsy.lua", "w") as f:
        f.write(lua_script)
        
    for pkg in packages:
        autoexec_path = f"/sdcard/Android/data/{pkg}/files/gloop/external/Autoexecute/arsy.lua"
        status_path = f"/sdcard/Android/data/{pkg}/files/gloop/workspace/arsy_status.txt"
        
        os.system(f"su -c 'mkdir -p \"$(dirname \"{autoexec_path}\")\"'")
        os.system(f"su -c 'cp temp_arsy.lua \"{autoexec_path}\"'")
        os.system(f"su -c 'rm -f \"{status_path}\"'")
        
    if os.path.exists("temp_arsy.lua"):
        os.remove("temp_arsy.lua")

def get_instances_telemetry(packages):
    instances = []
    current_time = int(time.time()) 
    
    for pkg in packages:
        workspace_path = f"/sdcard/Android/data/{pkg}/files/gloop/workspace/arsy_status.txt"
        try:
            output = subprocess.check_output(f"su -c 'cat \"{workspace_path}\"'", shell=True, stderr=subprocess.DEVNULL).decode('utf-8').strip()
            if "|" in output:
                parts = output.split("|")
                usn = parts[0]
                lua_time = int(parts[1])
                start_time = int(parts[2]) if len(parts) > 2 else lua_time
                
                uptime_sec = current_time - start_time
                hours, remainder = divmod(uptime_sec, 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
                
                if current_time - lua_time > 90:
                    status_icon = "🔴"
                    uptime_str = "Offline"
                else:
                    status_icon = "🟢"
                    
                instances.append({"usn": usn, "icon": status_icon, "uptime": uptime_str})
            else:
                instances.append({"usn": "Menunggu...", "icon": "⏳", "uptime": "Memuat..."})
        except:
            instances.append({"usn": "Login...", "icon": "⚫", "uptime": "Offline"})
            
    return instances
