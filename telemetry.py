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
    local UserInputService = game:GetService("UserInputService")
    local Workspace = game:GetService("Workspace")
    local SoundService = game:GetService("SoundService")

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

    -- ==========================================
    -- PENGHANCUR AUDIO & OPTIMASI GRAFIK
    -- ==========================================
    -- 1. Paksa Grafik ke Level Paling Rendah
    pcall(function()
        settings().Rendering.QualityLevel = Enum.QualityLevel.Level01
    end)

    -- 2. Fungsi Penghancur Audio (Menghapus file suara dari memori)
    local function destroyAudio()
        pcall(function()
            for _, v in pairs(Workspace:GetDescendants()) do
                if v:IsA("Sound") then v:Destroy() end
            end
            for _, v in pairs(SoundService:GetDescendants()) do
                if v:IsA("Sound") then v:Destroy() end
            end
        end)
    end
    
    -- Jalankan penghancur audio saat pertama kali mulai
    task.spawn(destroyAudio)

    -- 3. Tukang Sapu Otomatis (Setiap 10 Menit)
    task.spawn(function()
        while task.wait(600) do
            pcall(function()
                if clearconsole then clearconsole()
                elseif rconsoleclear then rconsoleclear()
                elseif consoleclear then consoleclear()
                end
                
                destroyAudio() -- Hancurkan audio baru yang mungkin muncul
                collectgarbage("collect") -- Bersihkan RAM
            end)
        end
    end)

    -- ==========================================
    -- UI SYSTEM: WIDGET SUPER MINI & BLACKSCREEN
    -- ==========================================
    task.spawn(function()
        pcall(function()
            local isBlackScreen = false
            
            local screenGui = Instance.new("ScreenGui")
            screenGui.Name = "BlackScreenWidget"
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

            -- KANVAS HITAM
            local blackFrame = Instance.new("Frame")
            blackFrame.Size = UDim2.new(1, 0, 1, 0) 
            blackFrame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
            blackFrame.Visible = false
            blackFrame.BorderSizePixel = 0
            blackFrame.Parent = screenGui

            -- TEKS PADA LAYAR HITAM (Tempat FPS & PING akan muncul)
            local afkText = Instance.new("TextLabel")
            afkText.Size = UDim2.new(1, 0, 1, 0)
            afkText.BackgroundTransparency = 1
            afkText.Text = "BLACK SCREEN MODE AKTIF"
            afkText.TextColor3 = Color3.fromRGB(80, 80, 80)
            afkText.TextSize = 22
            afkText.Font = Enum.Font.GothamBold
            afkText.Parent = blackFrame

            -- TOMBOL BULAT SUPER MINI (Ukurannya dipotong setengah!)
            local toggleBS = Instance.new("TextButton")
            toggleBS.Parent = screenGui
            toggleBS.BackgroundColor3 = Color3.fromRGB(50, 50, 200)
            toggleBS.BackgroundTransparency = 0.3 -- Sedikit lebih transparan agar tidak mengganggu
            toggleBS.Position = UDim2.new(1, -60, 0, 100)
            toggleBS.Size = UDim2.new(0, 35, 0, 35) -- Ukuran 35x35 (Sangat mungil)
            toggleBS.Font = Enum.Font.GothamBold
            toggleBS.Text = "BS" -- Teks disingkat saja
            toggleBS.TextColor3 = Color3.fromRGB(255, 255, 255)
            toggleBS.TextSize = 12
            toggleBS.BorderSizePixel = 0
            toggleBS.AutoButtonColor = false

            local cornerBS = Instance.new("UICorner")
            cornerBS.CornerRadius = UDim.new(1, 0)
            cornerBS.Parent = toggleBS

            -- SCRIPT GESER VS KLIK (SMART TOUCH DETECTOR)
            local dragging = false
            local dragInput, dragStart, startPos
            local isMoved = false

            toggleBS.InputBegan:Connect(function(input)
                if input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch then
                    dragging = true
                    isMoved = false
                    dragStart = input.Position
                    startPos = toggleBS.Position
                    
                    input.Changed:Connect(function()
                        if input.UserInputState == Enum.UserInputState.End then
                            dragging = false
                            if not isMoved then
                                isBlackScreen = not isBlackScreen
                                if isBlackScreen then
                                    blackFrame.Visible = true
                                    toggleBS.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
                                    if setfpscap then setfpscap(15) end -- FPS ditahan di 15 seperti sebelumnya
                                else
                                    blackFrame.Visible = false
                                    toggleBS.BackgroundColor3 = Color3.fromRGB(50, 50, 200)
                                    if setfpscap then setfpscap(60) end
                                end
                            end
                        end
                    end)
                end
            end)

            toggleBS.InputChanged:Connect(function(input)
                if input.UserInputType == Enum.UserInputType.MouseMovement or input.UserInputType == Enum.UserInputType.Touch then
                    dragInput = input
                end
            end)

            UserInputService.InputChanged:Connect(function(input)
                if input == dragInput and dragging then
                    local delta = input.Position - dragStart
                    if delta.Magnitude > 5 then
                        isMoved = true
                        toggleBS.Position = UDim2.new(startPos.X.Scale, startPos.X.Offset + delta.X, startPos.Y.Scale, startPos.Y.Offset + delta.Y)
                    end
                end
            end)

            -- RENDER STEPPED UNTUK FPS & PING (Hanya muncul di Black Screen)
            local sec = os.clock()
            local frames = 0
            game:GetService("RunService").RenderStepped:Connect(function()
                frames = frames + 1
                local currentSec = os.clock()
                if currentSec - sec >= 1 then
                    -- Jika sedang mode Black Screen, update teks di layar hitam
                    if isBlackScreen then
                        local ping = 0
                        pcall(function() ping = math.floor(Stats.Network.ServerStatsItem["Data Ping"]:GetValue()) end)
                        afkText.Text = "BLACK SCREEN MODE AKTIF\\n\\n" .. tostring(frames) .. " FPS   |   " .. tostring(ping) .. " ms"
                    end
                    frames = 0
                    sec = currentSec
                end
            end)
        end)
    end)

    -- ==========================================
    -- HEARTBEAT SYSTEM
    -- ==========================================
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
        
        workspaces = [
            f"/sdcard/Android/data/{pkg}/files/gloop/external/Workspace"
        ]
        
        os.system(f"su -c 'mkdir -p \"$(dirname \"{autoexec_path}\")\"'")
        for ws in workspaces:
            os.system(f"su -c 'mkdir -p \"{ws}\"'")
            os.system(f"su -c 'rm -f \"{ws}/arsy_status.txt\"'") 
            
        os.system(f"su -c 'cp \"{temp_file_path}\" \"{autoexec_path}\"'")
        
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

def get_instances_telemetry(packages):
    instances = []
    current_time = int(time.time()) 
    
    for pkg in packages:
        possible_paths = [
            f"/sdcard/Android/data/{pkg}/files/gloop/external/Workspace/arsy_status.txt"
        ]
        
        output = ""
        for path in possible_paths:
            try:
                result = subprocess.run(f"su -c 'cat \"{path}\"'", shell=True, capture_output=True, text=True)
                if "|" in result.stdout:
                    output = result.stdout.strip()
                    break 
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
