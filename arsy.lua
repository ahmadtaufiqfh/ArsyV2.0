task.spawn(function()
    repeat task.wait(2) until game:IsLoaded()
    
    local Players = game:GetService("Players")
    local player = Players.LocalPlayer
    while not player do task.wait(2) player = Players.LocalPlayer end
    
    local usn = player.Name
    local PORT = "8080"
    
    -- Mengirim sinyal instan ke Termux (0 beban memori HP)
    local function sendSignal(path, reason)
        local url = "http://127.0.0.1:" .. PORT .. path .. "?usn=" .. usn
        if reason then url = url .. "&reason=" .. string.gsub(reason, " ", "%%20") end
        pcall(function() game:HttpGetAsync(url) end)
    end

    -- Sensor Pindah Server / Reset
    player.OnTeleport:Connect(function()
        sendSignal("/warn", "SERVER_CHANGED")
    end)
    
    -- Sensor Error / Kick
    game:GetService("GuiService").ErrorMessageChanged:Connect(function(errMsg)
        local msg = errMsg:lower()
        if msg:find("kick") or msg:find("error") or msg:find("discon") or msg:find("sentinel") then
            sendSignal("/warn", "KICKED_OR_ERROR")
        end
    end)
    
    -- Sinyal Hidup (Ping) setiap 30 detik
    while true do
        sendSignal("/ping")
        task.wait(30)
    end
end)
