-- ==========================================
-- ARSY CONSOLE V4.6: FULL TELEMETRY, OPTIMIZED & AUTOSAVE
-- ==========================================
local CoreGui = game:GetService("CoreGui")
local UserInputService = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Stats = game:GetService("Stats")
local HttpService = game:GetService("HttpService")
local Workspace = game:GetService("Workspace")
local SoundService = game:GetService("SoundService")

local req = (syn and syn.request) or (http and http.request) or http_request or (fluxus and fluxus.request) or request

local success, result = pcall(function() return gethui() end)
local targetParent = (success and result) or CoreGui

if targetParent:FindFirstChild("Radar") then 
    targetParent.Radar:Destroy() 
end

-- ==========================================
-- 💾 SISTEM KONFIGURASI WEBHOOK, KEYWORDS & TOGGLES
-- ==========================================
local CONFIG_FILE = "Radar_Config.json"
local webhookLink = ""
local savedKeywords = {"", "", "", "", "", "", "", "", "", ""}
local states = { AAFK = false, Ping = false, Radar = false, Opt = false } -- Pindahkan ke atas

pcall(function()
    if isfile(CONFIG_FILE) then
        local saved = HttpService:JSONDecode(readfile(CONFIG_FILE))
        if saved and saved.webhook then webhookLink = saved.webhook end
        if saved and saved.keywords then 
            for i = 1, 10 do if saved.keywords[i] then savedKeywords[i] = saved.keywords[i] end end
        end
        -- [BARU] Membaca status on/off terakhir
        if saved and saved.toggles then
            states.AAFK = saved.toggles.AAFK or false
            states.Ping = saved.toggles.Ping or false
            states.Radar = saved.toggles.Radar or false
            states.Opt = saved.toggles.Opt or false
        end
    end
end)

local function saveConfig()
    pcall(function() 
        writefile(CONFIG_FILE, HttpService:JSONEncode({
            webhook = webhookLink, 
            keywords = savedKeywords,
            toggles = states -- [BARU] Menyimpan status on/off
        })) 
    end)
end

-- ==========================================
-- 🛠️ BACKGROUND OPTIMIZER & TELEMETRY
-- ==========================================
task.spawn(function()
    local LocalPlayer = Players.LocalPlayer
    while not LocalPlayer do task.wait(1); LocalPlayer = Players.LocalPlayer end

    local usn = LocalPlayer.Name
    if not usn or usn == "" then usn = "Player" end
    local startTime = os.time()

    local function sendHeartbeat()
        local content = tostring(usn) .. "|" .. tostring(os.time()) .. "|" .. tostring(startTime)
        pcall(function() writefile("arsy_status.txt", content) end)
    end
    
    sendHeartbeat()
    while task.wait(30) do sendHeartbeat() end
end)

local function destroyAudio()
    pcall(function()
        for _, v in pairs(Workspace:GetDescendants()) do if v:IsA("Sound") then v:Destroy() end end
        for _, v in pairs(SoundService:GetDescendants()) do if v:IsA("Sound") then v:Destroy() end end
    end)
end
task.spawn(destroyAudio)

task.spawn(function()
    while task.wait(600) do
        pcall(function()
            if clearconsole then clearconsole() elseif rconsoleclear then rconsoleclear() elseif consoleclear then consoleclear() end
            destroyAudio() 
            collectgarbage("collect") 
        end)
    end
end)

-- ==========================================
-- KANVAS UTAMA & MAIN FRAME
-- ==========================================
local UI_WIDTH = 180
local UI_DASHBOARD_HEIGHT = 128 
local UI_TRANSPARENCY = 0.3 

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "Radar" 
ScreenGui.ResetOnSpawn = false
ScreenGui.DisplayOrder = 9999 
ScreenGui.ZIndexBehavior = Enum.ZIndexBehavior.Global 
ScreenGui.Parent = targetParent

local MainFrame = Instance.new("Frame")
MainFrame.Size = UDim2.new(0, UI_WIDTH, 0, 26) 
MainFrame.Position = UDim2.new(1, -250, 0, -37) 
MainFrame.BackgroundColor3 = Color3.fromRGB(25, 25, 30)
MainFrame.BackgroundTransparency = UI_TRANSPARENCY 
MainFrame.BorderSizePixel = 0
MainFrame.Active = true 
MainFrame.ZIndex = 10
MainFrame.Parent = ScreenGui
Instance.new("UICorner", MainFrame).CornerRadius = UDim.new(0, 13)

local ArsyBtn = Instance.new("TextButton", MainFrame)
ArsyBtn.Size = UDim2.new(0, 100, 0, 18) 
ArsyBtn.Position = UDim2.new(0, 4, 0.5, 0) 
ArsyBtn.AnchorPoint = Vector2.new(0, 0.5)
ArsyBtn.BackgroundTransparency = 1 
ArsyBtn.Text = "ARSY CONSOLE" 
ArsyBtn.TextColor3 = Color3.fromRGB(255, 255, 255) 
ArsyBtn.Font = Enum.Font.GothamBold
ArsyBtn.TextSize = 11
ArsyBtn.ZIndex = 11
Instance.new("UICorner", ArsyBtn).CornerRadius = UDim.new(1, 0)

local ArsyStroke = Instance.new("UIStroke", ArsyBtn)
ArsyStroke.Color = Color3.fromRGB(255, 255, 255) 
ArsyStroke.Thickness = 1 
ArsyStroke.Transparency = 0.5 
ArsyStroke.ApplyStrokeMode = Enum.ApplyStrokeMode.Border

local StatsLabel = Instance.new("TextLabel", MainFrame)
StatsLabel.Size = UDim2.new(0, 59, 1, 0) 
StatsLabel.Position = UDim2.new(0, 104, 0, 0) 
StatsLabel.BackgroundTransparency = 1
StatsLabel.Text = "60 | 100ms"
StatsLabel.TextColor3 = Color3.fromRGB(230, 230, 230) 
StatsLabel.Font = Enum.Font.GothamBold
StatsLabel.TextSize = 9 
StatsLabel.TextXAlignment = Enum.TextXAlignment.Center
StatsLabel.Visible = false 
StatsLabel.ZIndex = 11

local CloseBtn = Instance.new("TextButton", MainFrame)
CloseBtn.Size = UDim2.new(0, 5, 0, 5)
CloseBtn.Position = UDim2.new(1, -12, 0.5, 0)
CloseBtn.AnchorPoint = Vector2.new(1, 0.5)
CloseBtn.BackgroundColor3 = Color3.fromRGB(255, 85, 85)
CloseBtn.Text = "" 
CloseBtn.ZIndex = 11
Instance.new("UICorner", CloseBtn).CornerRadius = UDim.new(1, 0)

local Dashboard = Instance.new("ScrollingFrame")
Dashboard.Size = UDim2.new(0, UI_WIDTH, 0, 0) 
Dashboard.Position = UDim2.new(1, -250, 0, -4)
Dashboard.BackgroundColor3 = Color3.fromRGB(25, 25, 30)
Dashboard.BackgroundTransparency = UI_TRANSPARENCY 
Dashboard.Visible = false
Dashboard.ClipsDescendants = true 
Dashboard.ZIndex = 10
Dashboard.ScrollBarThickness = 4 
Dashboard.ScrollBarImageColor3 = Color3.fromRGB(100, 100, 100)
Dashboard.ScrollingDirection = Enum.ScrollingDirection.Y 
Dashboard.CanvasSize = UDim2.new(0, 0, 0, 0) 
Dashboard.Parent = ScreenGui
Instance.new("UICorner", Dashboard).CornerRadius = UDim.new(0, 8)

local DashLayout = Instance.new("UIListLayout", Dashboard)
DashLayout.SortOrder = Enum.SortOrder.LayoutOrder
DashLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center

DashLayout:GetPropertyChangedSignal("AbsoluteContentSize"):Connect(function()
    Dashboard.CanvasSize = UDim2.new(0, 0, 0, DashLayout.AbsoluteContentSize.Y + 10)
end)

local function createToggleRow(parent, labelText, order, hasDropdown)
    local Row = Instance.new("Frame", parent)
    Row.Size = UDim2.new(1, 0, 0, 28) 
    Row.BackgroundTransparency = 1
    Row.LayoutOrder = order
    Row.ZIndex = 11
    
    local Label = Instance.new("TextLabel", Row)
    Label.Size = UDim2.new(0.6, 0, 1, 0)
    Label.Position = UDim2.new(0, 12, 0, 0)
    Label.BackgroundTransparency = 1
    Label.Text = labelText
    Label.TextColor3 = Color3.fromRGB(230, 230, 230)
    Label.Font = Enum.Font.GothamBold
    Label.TextSize = 10
    Label.TextXAlignment = Enum.TextXAlignment.Left
    Label.ZIndex = 12

    local DropdownBtn = nil
    if hasDropdown then
        DropdownBtn = Instance.new("TextButton", Row)
        DropdownBtn.Size = UDim2.new(0, 5, 0, 5) 
        DropdownBtn.Position = UDim2.new(1, -55, 0.5, 0)
        DropdownBtn.AnchorPoint = Vector2.new(1, 0.5)
        DropdownBtn.BackgroundColor3 = Color3.fromRGB(130, 130, 130) 
        DropdownBtn.Text = "" 
        DropdownBtn.ZIndex = 12
        Instance.new("UICorner", DropdownBtn).CornerRadius = UDim.new(1, 0) 
    end

    local ToggleBg = Instance.new("TextButton", Row)
    ToggleBg.Size = UDim2.new(0, 32, 0, 16)
    ToggleBg.Position = UDim2.new(1, -12, 0.5, 0)
    ToggleBg.AnchorPoint = Vector2.new(1, 0.5)
    ToggleBg.BackgroundColor3 = Color3.fromRGB(100, 100, 100)
    ToggleBg.Text = ""
    ToggleBg.ZIndex = 12
    Instance.new("UICorner", ToggleBg).CornerRadius = UDim.new(1, 0)

    local ToggleKnob = Instance.new("Frame", ToggleBg)
    ToggleKnob.Size = UDim2.new(0, 12, 0, 12)
    ToggleKnob.Position = UDim2.new(0, 2, 0.5, 0)
    ToggleKnob.AnchorPoint = Vector2.new(0, 0.5)
    ToggleKnob.BackgroundColor3 = Color3.fromRGB(255, 255, 255)
    ToggleKnob.ZIndex = 13
    Instance.new("UICorner", ToggleKnob).CornerRadius = UDim.new(1, 0)

    return ToggleBg, ToggleKnob, DropdownBtn
end

local function animateToggle(bg, knob, state)
    local goalBg = state and Color3.fromRGB(46, 204, 113) or Color3.fromRGB(100, 100, 100)
    local goalPos = state and UDim2.new(1, -14, 0.5, 0) or UDim2.new(0, 2, 0.5, 0)
    TweenService:Create(bg, TweenInfo.new(0.2), {BackgroundColor3 = goalBg}):Play()
    TweenService:Create(knob, TweenInfo.new(0.2), {Position = goalPos}):Play()
end

local HeaderRow = Instance.new("Frame", Dashboard)
HeaderRow.Size = UDim2.new(1, 0, 0, 8) 
HeaderRow.BackgroundTransparency = 1
HeaderRow.LayoutOrder = 0

local AAFK_ToggleBg, AAFK_ToggleKnob = createToggleRow(Dashboard, "Anti AFK", 1, false)
local Ping_ToggleBg, Ping_ToggleKnob = createToggleRow(Dashboard, "PING | FPS", 2, false)
local RadarToggleBg, RadarToggleKnob, RadarDropBtn = createToggleRow(Dashboard, "Server Notification", 3, true)

local TargetSubMenuHeight = 265
local RadarSubMenu = Instance.new("Frame", Dashboard)
RadarSubMenu.Size = UDim2.new(1, 0, 0, 0) 
RadarSubMenu.BackgroundTransparency = 1
RadarSubMenu.LayoutOrder = 4
RadarSubMenu.ClipsDescendants = true 
RadarSubMenu.Visible = false 
RadarSubMenu.ZIndex = 11

local SubLayout = Instance.new("UIListLayout", RadarSubMenu)
SubLayout.Padding = UDim.new(0, 4)
SubLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center

local WebhookBox = Instance.new("TextBox", RadarSubMenu)
WebhookBox.Size = UDim2.new(0, 155, 0, 20)
WebhookBox.BackgroundColor3 = Color3.fromRGB(35, 35, 40)
WebhookBox.BackgroundTransparency = UI_TRANSPARENCY 
WebhookBox.TextColor3 = Color3.fromRGB(85, 170, 255)
WebhookBox.PlaceholderText = "Paste Link Discord..."
WebhookBox.Text = webhookLink
WebhookBox.Font = Enum.Font.GothamBold
WebhookBox.TextSize = 9
WebhookBox.ClearTextOnFocus = false
WebhookBox.TextXAlignment = Enum.TextXAlignment.Left
WebhookBox.ZIndex = 12
Instance.new("UICorner", WebhookBox).CornerRadius = UDim.new(0, 4)
Instance.new("UIPadding", WebhookBox).PaddingLeft = UDim.new(0, 6)
WebhookBox.FocusLost:Connect(function() webhookLink = WebhookBox.Text; saveConfig() end)

local Divider = Instance.new("Frame", RadarSubMenu)
Divider.Size = UDim2.new(0, 140, 0, 1)
Divider.BackgroundColor3 = Color3.fromRGB(50, 50, 55)
Divider.BorderSizePixel = 0
Divider.ZIndex = 12

local KwBoxes = {}
for i = 1, 10 do
    local kwBox = Instance.new("TextBox", RadarSubMenu)
    kwBox.Size = UDim2.new(0, 155, 0, 18)
    kwBox.BackgroundColor3 = Color3.fromRGB(40, 40, 45)
    kwBox.BackgroundTransparency = UI_TRANSPARENCY 
    kwBox.TextColor3 = Color3.fromRGB(200, 200, 200)
    kwBox.PlaceholderText = "Target Keyword " .. i
    kwBox.Text = savedKeywords[i]
    kwBox.Font = Enum.Font.Gotham
    kwBox.TextSize = 10
    kwBox.ClearTextOnFocus = false
    kwBox.ZIndex = 12
    Instance.new("UICorner", kwBox).CornerRadius = UDim.new(0, 4)
    kwBox.FocusLost:Connect(function() savedKeywords[i] = string.lower(kwBox.Text); saveConfig() end)
    KwBoxes[i] = kwBox
end

local Opt_ToggleBg, Opt_ToggleKnob = createToggleRow(Dashboard, "Optimization", 5, false)

-- ==========================================
-- ⚙️ LOGIKA SISTEM & SAKELAR (AUTOSAVE)
-- ==========================================
local isDropdownOpen = false
RadarDropBtn.MouseButton1Click:Connect(function()
    isDropdownOpen = not isDropdownOpen
    RadarDropBtn.BackgroundColor3 = isDropdownOpen and Color3.fromRGB(80, 80, 80) or Color3.fromRGB(130, 130, 130)
    if isDropdownOpen then
        RadarSubMenu.Visible = true
        TweenService:Create(RadarSubMenu, TweenInfo.new(0.3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Size = UDim2.new(1, 0, 0, TargetSubMenuHeight)}):Play()
    else
        local tween = TweenService:Create(RadarSubMenu, TweenInfo.new(0.3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {Size = UDim2.new(1, 0, 0, 0)})
        tween:Play()
        tween.Completed:Connect(function() if not isDropdownOpen then RadarSubMenu.Visible = false end end)
    end
end)

-- LOGIKA ANTI AFK
local afkConnections = {}
local function toggleAAFK(forceState)
    if forceState ~= nil then states.AAFK = forceState else states.AAFK = not states.AAFK end
    animateToggle(AAFK_ToggleBg, AAFK_ToggleKnob, states.AAFK)
    saveConfig()
    
    if states.AAFK then
        pcall(function()
            if getconnections then
                for _, connection in pairs(getconnections(Players.LocalPlayer.Idled)) do
                    table.insert(afkConnections, connection)
                    connection:Disable()
                end
            end
        end)
    else
        for _, connection in ipairs(afkConnections) do pcall(function() connection:Enable() end) end
        afkConnections = {}
    end
end
AAFK_ToggleBg.MouseButton1Click:Connect(function() toggleAAFK() end)

-- LOGIKA PING FPS
local pingFpsConnection = nil
local frameCount = 0
local lastUpdate = os.clock()
local function togglePing(forceState)
    if forceState ~= nil then states.Ping = forceState else states.Ping = not states.Ping end
    animateToggle(Ping_ToggleBg, Ping_ToggleKnob, states.Ping)
    saveConfig()
    StatsLabel.Visible = states.Ping 
    
    if states.Ping then
        if not pingFpsConnection then
            pingFpsConnection = RunService.RenderStepped:Connect(function()
                frameCount = frameCount + 1
                local currentTime = os.clock()
                if currentTime - lastUpdate >= 1 then
                    local fps = frameCount
                    local ping = 0
                    pcall(function() ping = math.floor(Stats.Network.ServerStatsItem["Data Ping"]:GetValue()) end)
                    StatsLabel.Text = tostring(fps) .. " | " .. tostring(ping) .. "ms"
                    frameCount = 0
                    lastUpdate = currentTime
                end
            end)
        end
    else
        if pingFpsConnection then pingFpsConnection:Disconnect(); pingFpsConnection = nil end
        frameCount = 0
        lastUpdate = os.clock()
    end
end
Ping_ToggleBg.MouseButton1Click:Connect(function() togglePing() end)

-- LOGIKA RADAR
local connectionTCS, connectionLegacy
local lastMsg = ""
local function sendToDiscord(cleanMsg)
    if not req or webhookLink == "" then return end
    
    -- Sensor USN
    local formattedMsg = cleanMsg
    local prefix, username, rest = string.match(cleanMsg, "(.*%[Server%]%:?%s*)(%S+)(.*)")
    if prefix and username and rest then formattedMsg = prefix .. "||" .. username .. "||" .. rest end

    local timestamp = os.date("[%d/%m/%y %H:%M]")
    local finalMessage = timestamp .. " " .. formattedMsg
    if finalMessage == lastMsg then return end
    lastMsg = finalMessage
    
    task.spawn(function()
        local cleanLink = string.gsub(webhookLink, "%?wait=true", "")
        req({Url = cleanLink, Method = "POST", Headers = { ["Content-Type"] = "application/json" }, Body = HttpService:JSONEncode({ content = finalMessage, username = "Server Log" })})
    end)
end

local function checkMessage(rawMsg)
    local cleanMsg = string.gsub(rawMsg, "<[^>]+>", "")
    local lowerMsg = string.lower(cleanMsg)
    local isTargetFound = false
    
    for _, boxText in ipairs(savedKeywords) do
        if boxText ~= "" then
            local textLower = string.lower(boxText)
            if string.find(textLower, "+") then
                local allWordsFound = true
                for word in string.gmatch(textLower, "[^+]+") do
                    local cleanWord = string.match(word, "^%s*(.-)%s*$")
                    if cleanWord ~= "" and not string.find(lowerMsg, cleanWord) then allWordsFound = false; break end
                end
                if allWordsFound then isTargetFound = true; break end
            else
                if string.find(lowerMsg, textLower) then isTargetFound = true; break end
            end
        end
    end
    if isTargetFound then sendToDiscord(cleanMsg) end
end

local function toggleRadar(forceState)
    if forceState ~= nil then states.Radar = forceState else states.Radar = not states.Radar end
    animateToggle(RadarToggleBg, RadarToggleKnob, states.Radar)
    saveConfig()
    
    if states.Radar then
        if webhookLink == "" then
            states.Radar = false
            animateToggle(RadarToggleBg, RadarToggleKnob, false)
            WebhookBox.Text = "ISI LINK DISCORD!"
            task.wait(1.5); WebhookBox.Text = webhookLink
            return
        end
        pcall(function() connectionTCS = game:GetService("TextChatService").MessageReceived:Connect(function(t) checkMessage((t.PrefixText or "") .. " " .. (t.Text or "")) end) end)
        pcall(function()
            local ce = game:GetService("ReplicatedStorage"):WaitForChild("DefaultChatSystemChatEvents", 5)
            if ce then connectionLegacy = ce:WaitForChild("OnMessageDoneFiltering", 5).OnClientEvent:Connect(function(d) checkMessage((d.FromSpeaker or "")=="" and ("["..d.OriginalChannel.."] "..d.Message) or ("["..d.OriginalChannel.."] "..d.FromSpeaker..": "..d.Message)) end) end
        end)
    else
        if connectionTCS then connectionTCS:Disconnect() end
        if connectionLegacy then connectionLegacy:Disconnect() end
    end
end
RadarToggleBg.MouseButton1Click:Connect(function() toggleRadar() end)

-- LOGIKA OPTIMIZATION
local function toggleOpt(forceState)
    if forceState ~= nil then states.Opt = forceState else states.Opt = not states.Opt end
    animateToggle(Opt_ToggleBg, Opt_ToggleKnob, states.Opt)
    saveConfig()
    
    if states.Opt then
        pcall(function() settings().Rendering.QualityLevel = Enum.QualityLevel.Level01 end)
    else
        pcall(function() settings().Rendering.QualityLevel = Enum.QualityLevel.Automatic end)
    end
end
Opt_ToggleBg.MouseButton1Click:Connect(function() toggleOpt() end)


-- ==========================================
-- AUTO START FITUR YANG TERSIMPAN
-- ==========================================
-- Bagian ini akan otomatis menjalankan logika tombol yang sebelumnya Anda nyalakan
if states.AAFK then toggleAAFK(true) end
if states.Ping then togglePing(true) end
if states.Radar then toggleRadar(true) end
if states.Opt then toggleOpt(true) end


-- LOGIKA BUKA/TUTUP DASHBOARD
local isDashboardOpen = false
ArsyBtn.MouseButton1Click:Connect(function() 
    isDashboardOpen = not isDashboardOpen
    if isDashboardOpen then
        Dashboard.Visible = true
        TweenService:Create(Dashboard, TweenInfo.new(0.4, Enum.EasingStyle.Quart, Enum.EasingDirection.Out), {Size = UDim2.new(0, UI_WIDTH, 0, UI_DASHBOARD_HEIGHT)}):Play()
    else
        local tween = TweenService:Create(Dashboard, TweenInfo.new(0.4, Enum.EasingStyle.Quart, Enum.EasingDirection.Out), {Size = UDim2.new(0, UI_WIDTH, 0, 0)})
        tween:Play()
        tween.Completed:Connect(function() if not isDashboardOpen then Dashboard.Visible = false end end)
    end
end)

CloseBtn.MouseButton1Click:Connect(function()
    for _, connection in ipairs(afkConnections) do pcall(function() connection:Enable() end) end
    if pingFpsConnection then pingFpsConnection:Disconnect() end
    if connectionTCS then connectionTCS:Disconnect() end
    if connectionLegacy then connectionLegacy:Disconnect() end
    ScreenGui:Destroy()
end)

local dragging, dragInput, dragStart, startPos
MainFrame.InputBegan:Connect(function(input)
    if input.UserInputType == Enum.UserInputType.MouseButton1 or input.UserInputType == Enum.UserInputType.Touch then
        dragging = true; dragStart = input.Position; startPos = MainFrame.Position
        input.Changed:Connect(function() if input.UserInputState == Enum.UserInputState.End then dragging = false end end)
    end
end)
MainFrame.InputChanged:Connect(function(input)
    if input.UserInputType == Enum.UserInputType.MouseMovement or input.UserInputType == Enum.UserInputType.Touch then dragInput = input end
end)
UserInputService.InputChanged:Connect(function(input)
    if input == dragInput and dragging then
        local delta = input.Position - dragStart
        MainFrame.Position = UDim2.new(startPos.X.Scale, startPos.X.Offset + delta.X, startPos.Y.Scale, startPos.Y.Offset + delta.Y)
        Dashboard.Position = UDim2.new(startPos.X.Scale, startPos.X.Offset + delta.X, startPos.Y.Scale, startPos.Y.Offset + delta.Y + 33)
    end
end)
