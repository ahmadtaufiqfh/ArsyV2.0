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
    local RunService = game:GetService("RunService")
    local Stats = game:GetService("Stats")

    local LocalPlayer = Players.LocalPlayer
    while not LocalPlayer do
        task.wait(1)
        LocalPlayer = Players.LocalPlayer
    end

    local usn = LocalPlayer.Name
    local startTime = os.time()

    pcall(function()
        for _, connection in pairs(getconnections(LocalPlayer.Idled)) do
            connection:Disable()
        end
    end)

    task.spawn(function()
        while task.wait(900) do
            pcall(function()
                local char = LocalPlayer.Character
                if char and char:FindFirstChild("HumanoidRootPart") then
                    local hrp = char.HumanoidRootPart
                    hrp.CFrame = hrp.CFrame * CFrame.new(0, 0.1, 0) 
                    task.wait(0.5)
                    hrp.CFrame = hrp.CFrame * CFrame.new(0, -0.1, 0)
                end
            end)
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
            blackFrame.Position = UDim2.new(0, 0, 0, 0)
            blackFrame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
            blackFrame.Visible = false
            blackFrame.BorderSizePixel = 0
            blackFrame.Parent = screenGui

            local afkText = Instance.new("TextLabel")
            afkText.Size = UDim2.new(1, 0, 1, 0)
            afkText.BackgroundTransparency = 1
            afkText.Text = "BLACK SCREEN MODE"
            afkText.TextColor3 = Color3.fromRGB(80, 80, 80)
            afkText.TextSize = 20
            afkText.Font = Enum.Font.GothamBold
            afkText.Parent = blackFrame

            local toggleButton = Instance.new("TextButton")
            toggleButton.Parent = screenGui
            toggleButton.BackgroundColor3 = Color3.fromRGB(50, 50, 200)
            toggleButton.Position = UDim2.new(1, -180, 0, 100)
            toggleButton.Size = UDim2.new(0, 160, 0, 40)
            toggleButton.Font = Enum.Font.GothamBold
            toggleButton.Text = "Loading..." 
            toggleButton.TextColor3 = Color3.fromRGB(255, 255, 255)
            toggleButton.TextSize = 14.000 
            toggleButton.Draggable = true 
            toggleButton.AutoButtonColor = false

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

            RunService.RenderStepped:Connect(function()
                frames = frames + 1
                local currentSec = os.clock()
                if currentSec - sec >= 1 then
                    local fps = frames
                    local status = isBlackScreen and "ON" or "OFF"
                    local ping = 0
                    pcall(function() ping = math.floor(Stats.Network.ServerStatsItem["Data Ping"]:GetValue()) end)
                    toggleButton.Text = status .. " | " .. tostring(fps) .. " | " .. tostring(ping) .. "ms"
                    frames = 0
                    sec = currentSec
                end
            end)
            
            game.StarterGui:SetCore("SendNotification", {
                Title = "ARSY V2.0",
                Text = "Black Screen & Telemetry Aktif!",
                Duration = 5
            })
        end)
    end)

    -- ==========================================
    -- 4. HEARTBEAT SYSTEM (PERBAIKAN DISCORD)
    -- ==========================================
    task.spawn(function()
        -- Membuat fungsi khusus untuk mengirim data
        local function sendHeartbeat()
            pcall(function()
                writefile("arsy_status.txt", usn .. "|" .. tostring(os.time()) .. "|" .. tostring(startTime))
            end)
        end
        
        -- EKSEKUSI SEKETIKA: Termux langsung tahu Anda Online dan memicu Discord!
        sendHeartbeat()
        
        -- Kemudian baru diulang setiap 30 detik
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
        status_path = f"/sdcard/Android/data/{pkg}/files/gloop/workspace/arsy_status.txt"
        
        os.system(f"su -c 'mkdir -p \"$(dirname \"{autoexec_path}\")\"'")
        os.system(f"su -c 'cp \"{temp_file_path}\" \"{autoexec_path}\"'")
        
        # PENTING: File status lama dihapus agar saat game memuat ulang statusnya benar-benar direset.
        os.system(f"su -c 'rm -f \"{status_path}\"'")
        
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

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
