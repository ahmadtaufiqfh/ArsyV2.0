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
    -- UI SYSTEM (MINI DUAL MODE + DRAGGABLE)
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

            -- KANVAS HITAM (Untuk Blackscreen)
            local blackFrame = Instance.new("Frame")
            blackFrame.Size = UDim2.new(1, 0, 1, 0) 
            blackFrame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
            blackFrame.Visible = false
            blackFrame.BorderSizePixel = 0
            blackFrame.Parent = screenGui

            local afkText = Instance.new("TextLabel")
            afkText.Size = UDim2.new(1, 0, 1, 0)
            afkText.BackgroundTransparency = 1
            afkText.Text = "BLACK SCREEN & POTATO MODE AKTIF"
            afkText.TextColor3 = Color3.fromRGB(80, 80, 80)
            afkText.TextSize = 20
            afkText.Font = Enum.Font.GothamBold
            afkText.Parent = blackFrame

            -- WADAH TOMBOL (Agar bisa digeser bersamaan)
            local dragMenu = Instance.new("Frame")
            dragMenu.Name = "DragMenu"
            dragMenu.Parent = screenGui
            dragMenu.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
            dragMenu.BackgroundTransparency = 1 -- Transparan, hanya tombol yang terlihat
            dragMenu.Position = UDim2.new(1, -130, 0, 80)
            dragMenu.Size = UDim2.new(0, 115, 0, 65) -- Setengah ukuran dari sebelumnya!
            dragMenu.Active = true
            dragMenu.Draggable = true -- FITUR GESER AKTIF

            -- TOMBOL 1: BLACK SCREEN (Ukuran Mini)
            local toggleBS = Instance.new("TextButton")
            toggleBS.Parent = dragMenu
            toggleBS.BackgroundColor3 = Color3.fromRGB(50, 50, 200)
            toggleBS.Position = UDim2.new(0, 0, 0, 0)
            toggleBS.Size = UDim2.new(1, 0, 0, 30)
            toggleBS.Font = Enum.Font.GothamBold
            toggleBS.Text = "Loading..." 
            toggleBS.TextColor3 = Color3.fromRGB(255, 255, 255)
            toggleBS.TextSize = 10 -- Teks dikecilkan agar muat
            
            local cornerBS = Instance.new("UICorner")
            cornerBS.CornerRadius = UDim.new(0, 6)
            cornerBS.Parent = toggleBS

            -- TOMBOL 2: POTATO MODE (Ukuran Mini)
            local togglePotato = Instance.new("TextButton")
            togglePotato.Parent = dragMenu
            togglePotato.BackgroundColor3 = Color3.fromRGB(50, 50, 200)
            togglePotato.Position = UDim2.new(0, 0, 0, 35) -- Berada pas di bawah tombol BS
            togglePotato.Size = UDim2.new(1, 0, 0, 30)
            togglePotato.Font = Enum.Font.GothamBold
            togglePotato.Text = "POTATO: OFF" 
            togglePotato.TextColor3 = Color3.fromRGB(255, 255, 255)
            togglePotato.TextSize = 10 
            
            local cornerPotato = Instance.new("UICorner")
            cornerPotato.CornerRadius = UDim.new(0, 6)
            cornerPotato.Parent = togglePotato

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
