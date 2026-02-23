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
    -- OPTIMASI AMAN: RATA KIRI, RAM, & CONSOLE
    -- ==========================================
    -- 1. Paksa Grafik ke Level Paling Rendah (Rata Kiri)
    pcall(function()
        settings().Rendering.QualityLevel = Enum.QualityLevel.Level01
    end)

    -- 2. Tukang Sapu Otomatis (Setiap 10 Menit)
    task.spawn(function()
        while task.wait(600) do
            pcall(function()
                -- Bersihkan log console yang menumpuk
                if clearconsole then clearconsole()
                elseif rconsoleclear then rconsoleclear()
                elseif consoleclear then consoleclear()
                end
                
                -- Bersihkan memori RAM dari sampah data
                collectgarbage("collect")
            end)
        end
    end)

    -- ==========================================
    -- UI SYSTEM: FLOATING WIDGET BULAT (DRAGGABLE)
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

            local afkText = Instance.new("TextLabel")
            afkText.Size = UDim2.new(1, 0, 1, 0)
            afkText.BackgroundTransparency = 1
            afkText.Text = "BLACK SCREEN MODE AKTIF"
            afkText.TextColor3 = Color3.fromRGB(80, 80, 80)
            afkText.TextSize = 20
            afkText.Font = Enum.Font.GothamBold
            afkText.Parent = blackFrame

            -- TOMBOL BULAT (FLOATING WIDGET)
            local toggleBS = Instance.new("TextButton")
            toggleBS.Parent = screenGui
            toggleBS.BackgroundColor3 = Color3.fromRGB(50, 50, 200)
            toggleBS.BackgroundTransparency = 0.1 -- Sedikit transparan agar elegan
            toggleBS.Position = UDim2.new(1, -90, 0, 100)
            toggleBS.Size = UDim2.new(0, 65, 0, 65) -- Ukuran kotak proporsional
            toggleBS.Font = Enum.Font.GothamBold
            toggleBS.Text = "BS: OFF\\n--\\n--" 
            toggleBS.TextColor3 = Color3.fromRGB(255, 255, 255)
            toggleBS.TextSize = 11
            toggleBS.BorderSizePixel = 0
            toggleBS.AutoButtonColor = false -- Matikan efek klik bawaan

            -- Rahasia bentuk bulat sempurna: CornerRadius = 1 (100%)
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
                            -- Jika jari dilepas dan tombol TIDAK digeser, maka dihitung sebagai KLIK (Toggle)
                            if not isMoved then
                                isBlackScreen = not isBlackScreen
                                if isBlackScreen then
                                    blackFrame.Visible = true
                                    toggleBS.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
                                    if setfpscap then setfpscap(15) end -- FPS diturunkan ke 15 saat BS untuk hemat RAM ekstrem
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
                    -- Jika jari bergeser lebih dari 5 pixel, maka dihitung sebagai GESER (Bukan Klik)
                    if delta.Magnitude > 5 then
                        isMoved = true
                        toggleBS.Position = UDim2.new(startPos.X.Scale, startPos.X.Offset + delta.X, startPos.Y.Scale, startPos.Y.Offset + delta.Y)
                    end
                end
            end)

            -- RENDER STEPPED UNTUK FPS & PING DI DALAM TOMBOL
            local sec = os.clock()
            local frames = 0
            game:GetService("RunService").RenderStepped:Connect(function()
                frames = frames + 1
                local currentSec = os.clock()
                if currentSec - sec >= 1 then
                    local ping = 0
                    pcall(function() ping = math.floor(Stats.Network.ServerStatsItem["Data Ping"]:GetValue()) end)
                    -- Menulis 3 baris di dalam tombol bulat
                    local statusText = isBlackScreen and "BS: ON" or "BS: OFF"
                    toggleBS.Text = statusText .. "\\n" .. tostring(frames) .. " FPS\\n" .. tostring(ping) .. " ms"
                    
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
