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
    -- AUTO-CLEAN RAM & CONSOLE (Setiap 10 Menit)
    -- ==========================================
    task.spawn(function()
        while task.wait(600) do
            pcall(function()
                if clearconsole then clearconsole()
                elseif rconsoleclear then rconsoleclear()
                elseif consoleclear then consoleclear()
                end
                collectgarbage("collect")
            end)
        end
    end)

    -- ==========================================
    -- UI SYSTEM (SUPER MINI + TOUCH DRAG)
    -- ==========================================
    task.spawn(function()
        pcall(function()
            local isBlackScreen = false
            local isPotato = false
            
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
            afkText.Text = "BLACKSCREEN MODE"
            afkText.TextColor3 = Color3.fromRGB(80, 80, 80)
            afkText.TextSize = 20
            afkText.Font = Enum.Font.GothamBold
            afkText.Parent = blackFrame

            -- WADAH UTAMA (Ukuran super kecil: 100x65)
            local dragMenu = Instance.new("Frame")
            dragMenu.Name = "DragMenu"
            dragMenu.Parent = screenGui
            dragMenu.BackgroundColor3 = Color3.fromRGB(30, 30, 30)
            dragMenu.Position = UDim2.new(1, -110, 0, 80)
            dragMenu.Size = UDim2.new(0, 100, 0, 65)
            dragMenu.BorderSizePixel = 0
            
            local cornerMenu = Instance.new("UICorner")
            cornerMenu.CornerRadius = UDim.new(0, 6)
            cornerMenu.Parent = dragMenu

            -- GAGANG GESER (DRAG HANDLE)
            local dragBar = Instance.new("TextLabel")
            dragBar.Parent = dragMenu
            dragBar.Size = UDim2.new(1, 0, 0, 15)
            dragBar.BackgroundColor3 = Color3.fromRGB(20, 20, 20)
            dragBar.TextColor3 = Color3.fromRGB(150, 150, 150)
            dragBar.Text = "✥ GESER ✥"
            dragBar.Font = Enum.Font.GothamBold
            dragBar.TextSize = 8
            dragBar.Active = true -- Penting untuk deteksi sentuhan
            
            local cornerBar = Instance.new("UICorner")
            cornerBar.CornerRadius = UDim.new(0, 6)
            cornerBar.Parent = dragBar
            
            -- Menutupi sudut bawah gagang agar rata dengan tombol
            local barCover = Instance.new("Frame")
            barCover.Parent = dragBar
            barCover.Size = UDim2.new(1, 0, 0, 3)
            barCover.Position = UDim2.new(0, 0, 1, -3)
            barCover.BackgroundColor3 = Color3.fromRGB(20, 20, 20)
            barCover.BorderSizePixel = 0

            -- TOMBOL 1: BLACK SCREEN
            local toggleBS = Instance.new("TextButton")
            toggleBS.Parent = dragMenu
            toggleBS.BackgroundColor3 = Color3.fromRGB(50, 50, 200)
            toggleBS.Position = UDim2.new(0, 0, 0, 15)
            toggleBS.Size = UDim2.new(1, 0, 0, 25)
            toggleBS.Font = Enum.Font.GothamBold
            toggleBS.Text = "BS: OFF" 
            toggleBS.TextColor3 = Color3.fromRGB(255, 255, 255)
            toggleBS.TextSize = 9
            toggleBS.BorderSizePixel = 0

            -- TOMBOL 2: POTATO MODE
            local togglePotato = Instance.new("TextButton")
            togglePotato.Parent = dragMenu
            togglePotato.BackgroundColor3 = Color3.fromRGB(50, 50, 200)
            togglePotato.Position = UDim2.new(0, 0, 0, 40)
            togglePotato.Size = UDim2.new(1, 0, 0, 25)
            togglePotato.Font = Enum.Font.GothamBold
            togglePotato.Text = "POTATO: OFF" 
            togglePotato.TextColor3 = Color3.fromRGB(255, 255, 255)
            togglePotato.TextSize = 9
            togglePotato.BorderSizePixel = 0
            
            local cornerPotato = Instance.new("UICorner")
            cornerPotato.CornerRadius = UDim.new(0, 6)
            cornerPotato.Parent = togglePotato
            
            local potatoCover = Instance.new("Frame")
            potatoCover.Parent = togglePotato
            potatoCover.Size = UDim2.new(1, 0, 0, 3)
            potatoCover.Position = UDim2.new(0, 0, 0, 0)
            potatoCover.BackgroundColor3 = togglePotato.BackgroundColor3
            potatoCover.BorderSizePixel = 0

            -- SCRIPT GESER KHUSUS MOBILE (TOUCH SUPPORT)
            local dragging = false
            local dragInput, dragStart, startPos

            dragBar.InputBegan:Connect(function(input)
                if input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch then
                    dragging = true
                    dragStart = input.Position
                    startPos = dragMenu.Position
                    
                    input.Changed:Connect(function()
                        if input.UserInputState == Enum.UserInputState.End then
                            dragging = false
                        end
                    end)
                end
            end)

            dragBar.InputChanged:Connect(function(input)
                if input.UserInputType == Enum.UserInputType.MouseMovement or input.UserInputType == Enum.UserInputType.Touch then
                    dragInput = input
                end
            end)

            UserInputService.InputChanged:Connect(function(input)
                if input == dragInput and dragging then
                    local delta = input.Position - dragStart
                    dragMenu.Position = UDim2.new(startPos.X.Scale, startPos.X.Offset + delta.X, startPos.Y.Scale, startPos.Y.Offset + delta.Y)
                end
            end)

            -- FUNGSI KLIK BLACK SCREEN
            toggleBS.MouseButton1Click:Connect(function()
                isBlackScreen = not isBlackScreen
                if isBlackScreen then
                    blackFrame.Visible = true
                    toggleBS.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
                    if setfpscap then setfpscap(30) end
                else
                    blackFrame.Visible = false
                    toggleBS.BackgroundColor3 = Color3.fromRGB(50, 50, 200)
                    if setfpscap then setfpscap(60) end
                end
            end)

            -- FUNGSI KLIK POTATO MODE
            togglePotato.MouseButton1Click:Connect(function()
                isPotato = not isPotato
                if isPotato then
                    togglePotato.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
                    potatoCover.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
                    togglePotato.Text = "POTATO: ON"
                    
                    pcall(function()
                        local lighting = game:GetService("Lighting")
                        lighting.GlobalShadows = false
                        lighting.FogEnd = 9e9
                        
                        for _, v in pairs(game:GetService("Workspace"):GetDescendants()) do
                            if v:IsA("BasePart") and not v.Parent:FindFirstChild("Humanoid") then
                                v.Material = Enum.Material.SmoothPlastic
                                v.Reflectance = 0
                            elseif v:IsA("Decal") or v:IsA("Texture") or v:IsA("ParticleEmitter") or v:IsA("Trail") then
                                v:Destroy()
                            end
                        end
                    end)
                else
                    togglePotato.BackgroundColor3 = Color3.fromRGB(50, 50, 200)
                    potatoCover.BackgroundColor3 = Color3.fromRGB(50, 50, 200)
                    togglePotato.Text = "POTATO: OFF"
                    
                    pcall(function()
                        game:GetService("Lighting").GlobalShadows = true
                    end)
                end
            end)

            -- RENDER STEPPED UNTUK FPS & PING
            local sec = os.clock()
            local frames = 0
            game:GetService("RunService").RenderStepped:Connect(function()
                frames = frames + 1
                local currentSec = os.clock()
                if currentSec - sec >= 1 then
                    local ping = 0
                    pcall(function() ping = math.floor(Stats.Network.ServerStatsItem["Data Ping"]:GetValue()) end)
                    toggleBS.Text = "BS: " .. (isBlackScreen and "ON" or "OFF") .. " | " .. tostring(frames) .. " | " .. tostring(ping) .. "ms"
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
