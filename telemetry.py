import os
import time
import subprocess

def deploy_telemetry_lua(packages):
    # ==========================================
    # FILE 1: CORE SYSTEM (ANTI-AFK & HEARTBEAT)
    # ==========================================
    lua_core = """
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

-- HEARTBEAT (FIXED: Dibungkus task.spawn agar tidak nge-block autoexec)
task.spawn(function()
    while task.wait(30) do
        pcall(function()
            writefile("arsy_status.txt", usn .. "|" .. tostring(os.time()) .. "|" .. tostring(startTime))
        end)
    end
end)
"""

    # ==========================================
    # FILE 2: UI SYSTEM (BLACK SCREEN & MONITOR)
    # ==========================================
    lua_ui = """
repeat task.wait() until game:IsLoaded()
local CoreGui = game:GetService("CoreGui")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Stats = game:GetService("Stats")

local isBlackScreen = false

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "BlackScreen"
screenGui.IgnoreGuiInset = true 
screenGui.DisplayOrder = 2147483647

if pcall(function() screenGui.Parent = CoreGui end) then 
else 
    screenGui.Parent = Players.LocalPlayer:WaitForChild("PlayerGui") 
end

local blackFrame = Instance.new("Frame")
blackFrame.Name = "BlackCanvas"
blackFrame.Size = UDim2.new(1, 0, 1, 0) 
blackFrame.Position = UDim2.new(0, 0, 0, 0)
blackFrame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
blackFrame.Visible = false
blackFrame.BorderSizePixel = 0
blackFrame.Parent = screenGui

local afkText = Instance.new("TextLabel")
afkText.Name = "AFKText"
afkText.Size = UDim2.new(1, 0, 1, 0)
afkText.BackgroundTransparency = 1
afkText.Text = "BLACK SCREEN MODE"
afkText.TextColor3 = Color3.fromRGB(80, 80, 80)
afkText.TextSize = 20
afkText.Font = Enum.Font.GothamBold
afkText.Parent = blackFrame

local toggleButton = Instance.new("TextButton")
toggleButton.Name = "ToggleButton"
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
        
        pcall(function()
            ping = math.floor(Stats.Network.ServerStatsItem["Data Ping"]:GetValue())
        end)
        
        toggleButton.Text = status .. " | " .. tostring(fps) .. " | " .. tostring(ping) .. "ms"
        frames = 0
        sec = currentSec
    end
end)

game.StarterGui:SetCore("SendNotification", {
    Title = "BLACK SCREEN MODE",
    Text = "Black screen mode ready!",
    Duration = 5
})
"""

    with open("temp_core.lua", "w", encoding="utf-8") as f_core:
        f_core.write(lua_core)
        
    with open("temp_ui.lua", "w", encoding="utf-8") as f_ui:
        f_ui.write(lua_ui)
        
    for pkg in packages:
        core_path = f"/sdcard/Android/data/{pkg}/files/gloop/external/Autoexecute/1_arsy_core.lua"
        ui_path = f"/sdcard/Android/data/{pkg}/files/gloop/external/Autoexecute/2_arsy_ui.lua"
        status_path = f"/sdcard/Android/data/{pkg}/files/gloop/workspace/arsy_status.txt"
        old_arsy_path = f"/sdcard/Android/data/{pkg}/files/gloop/external/Autoexecute/arsy.lua"
        
        # Hapus file arsy.lua yang lama agar tidak bentrok
        os.system(f"su -c 'rm -f \"{old_arsy_path}\"'")
        
        os.system(f"su -c 'mkdir -p \"$(dirname \"{core_path}\")\"'")
        os.system(f"su -c 'cp temp_core.lua \"{core_path}\"'")
        os.system(f"su -c 'cp temp_ui.lua \"{ui_path}\"'")
        os.system(f"su -c 'rm -f \"{status_path}\"'")
        
    if os.path.exists("temp_core.lua"): os.remove("temp_core.lua")
    if os.path.exists("temp_ui.lua"): os.remove("temp_ui.lua")


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
