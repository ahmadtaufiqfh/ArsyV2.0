import os
import time
import subprocess

def deploy_telemetry_lua(packages):
    lua_script = """
local function InitArsy()
    if not game:IsLoaded() then
        game.Loaded:Wait()
    end
    task.wait(2)

    local Players = game:GetService("Players")
    local CoreGui = game:GetService("CoreGui")
    local Stats = game:GetService("Stats")

    local LocalPlayer = Players.LocalPlayer
    while not LocalPlayer do
        task.wait(1)
        LocalPlayer = Players.LocalPlayer
    end

    local usn = LocalPlayer.Name
    if not usn or usn == "" then usn = "Player" end
    local startTime = os.time()

    pcall(function()
        for _, connection in pairs(getconnections(LocalPlayer.Idled)) do
            connection:Disable()
        end
    end)

    task.spawn(function()
        pcall(function()
            local isBlackScreen = false
            local screenGui = Instance.new("ScreenGui")
            screenGui.Name = "BlackScreen"
            screenGui.IgnoreGuiInset = true 
            screenGui.DisplayOrder = 2147483647
            screenGui.ResetOnSpawn = false

            local ui_parent
            local successHui, resultHui = pcall(function() return gethui() end)
            if successHui and resultHui then
                ui_parent = resultHui
            else
                ui_parent = CoreGui
            end
            screenGui.Parent = ui_parent

            local blackFrame = Instance.new("Frame")
            blackFrame.Size = UDim2.new(1, 0, 1, 0) 
            blackFrame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
            blackFrame.Visible = false
            blackFrame.BorderSizePixel = 0
            blackFrame.Parent = screenGui

            local toggleButton = Instance.new("TextButton")
            toggleButton.Parent = screenGui
            toggleButton.BackgroundColor3 = Color3.fromRGB(50, 50, 200)
            toggleButton.Position = UDim2.new(1, -180, 0, 100)
            toggleButton.Size = UDim2.new(0, 160, 0, 40)
            toggleButton.Font = Enum.Font.GothamBold
            toggleButton.Text = "Loading..." 
            toggleButton.TextColor3 = Color3.fromRGB(255, 255, 255)
            toggleButton.TextSize = 14.000 
            
            local uiCorner = Instance.new("UICorner")
            uiCorner.CornerRadius = UDim.new(0, 8)
            uiCorner.Parent = toggleButton

            toggleButton.MouseButton1Click:Connect(function()
                isBlackScreen = not isBlackScreen
                if isBlackScreen then
                    blackFrame.Visible = true
                    toggleButton.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
                    if setfpscap then setfpscap(30) end
                else
                    blackFrame.Visible = false
                    toggleButton.BackgroundColor3 = Color3.fromRGB(50, 50, 200)
                    if setfpscap then setfpscap(60) end
                end
            end)

            local sec = os.clock()
            local frames = 0
            game:GetService("RunService").RenderStepped:Connect(function()
                frames = frames + 1
                local currentSec = os.clock()
                if currentSec - sec >= 1 then
                    local ping = 0
                    pcall(function() ping = math.floor(Stats.Network.ServerStatsItem["Data Ping"]:GetValue()) end)
                    toggleButton.Text = (isBlackScreen and "ON" or "OFF") .. " | " .. tostring(frames) .. " | " .. tostring(ping) .. "ms"
                    frames = 0
                    sec = currentSec
                end
            end)
        end)
    end)

    task.spawn(function()
        local function sendHeartbeat()
            local content = tostring(usn) .. "|" .. tostring(os.time()) .. "|" .. tostring(startTime)
            pcall(function()
                writefile("arsy_status.txt", content)
            end)
        end
        
        sendHeartbeat()
        while task.wait(30) do
            sendHeartbeat()
        end
    end)
end

task.spawn(InitArsy)
"""
    current_dir = os.getcwd()
    temp_file_path = os.path.join(current_dir, "temp_arsy.lua")

    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write(lua_script)
        
    for pkg in packages:
        autoexec_path = f"/sdcard/Android/data/{pkg}/files/gloop/external/Autoexecute/arsy.lua"
        
        # MEMBUAT SEMUA KEMUNGKINAN FOLDER AGAR TIDAK ERROR
        workspaces = [
            f"/sdcard/Android/data/{pkg}/files/gloop/workspace",
            f"/sdcard/Android/data/{pkg}/files/delta/workspace",
            f"/sdcard/Android/data/{pkg}/files/spdm/workspace",
            f"/sdcard/Android/data/{pkg}/files/codex/workspace",
            f"/sdcard/Android/data/{pkg}/files/hydrogen/workspace"
        ]
        
        os.system(f"su -c 'mkdir -p \"$(dirname \"{autoexec_path}\")\"'")
        for ws in workspaces:
            os.system(f"su -c 'mkdir -p \"{ws}\"'")
            os.system(f"su -c 'rm -f \"{ws}/arsy_status.txt\"'") # Bersihkan sisa data lama
            
        os.system(f"su -c 'cp \"{temp_file_path}\" \"{autoexec_path}\"'")
        
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

def get_instances_telemetry(packages):
    instances = []
    current_time = int(time.time()) 
    
    for pkg in packages:
        # RADAR: MENCARI FILE DI SEMUA FOLDER EXECUTOR POPULER
        possible_paths = [
            f"/sdcard/Android/data/{pkg}/files/gloop/workspace/arsy_status.txt",
            f"/sdcard/Android/data/{pkg}/files/delta/workspace/arsy_status.txt",
            f"/sdcard/Android/data/{pkg}/files/spdm/workspace/arsy_status.txt",
            f"/sdcard/Android/data/{pkg}/files/codex/workspace/arsy_status.txt",
            f"/sdcard/Delta/workspace/arsy_status.txt"
        ]
        
        output = ""
        for path in possible_paths:
            try:
                result = subprocess.run(f"su -c 'cat \"{path}\"'", shell=True, capture_output=True, text=True)
                if "|" in result.stdout:
                    output = result.stdout.strip()
                    break # FILE KETEMU! Berhenti mencari.
            except:
                continue
        
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
            instances.append({"usn": "Menunggu Data...", "icon": "⏳", "uptime": "Memuat..."})
            
    return instances
