task.spawn(function()
    repeat task.wait(2) until game:IsLoaded()
    
    local Players = game:GetService("Players")
    local player = Players.LocalPlayer
    while not player do
        task.wait(2)
        player = Players.LocalPlayer
    end
    
    local usn = player.Name
    local currentJobId = game.JobId
    
    -- 🚨 1. SISTEM SIDIK JARI (JOBID LOCKING)
    local lockFile = "arsy_lock_" .. usn .. ".txt"
    local isWrongServer = false
    
    pcall(function()
        if isfile(lockFile) then
            -- Jika sudah ada sidik jari, bandingkan!
            local savedJobId = readfile(lockFile)
            if currentJobId ~= savedJobId and currentJobId ~= "" then
                isWrongServer = true
            end
        else
            -- Jika belum ada, simpan sidik jari server ini
            writefile(lockFile, currentJobId)
        end
    end)
    
    -- Jika ketahuan pindah server (sidik jari beda), bunyikan alarm
    if isWrongServer then
        pcall(function()
            writefile("arsy_warn_" .. usn .. ".txt", "SERVER_CHANGED")
        end)
        return 
    end
    
    -- 🟢 2. SINYAL AMAN (Kirim jika server masih sama)
    pcall(function()
        writefile("arsy_usn_" .. usn .. ".txt", "aktif")
    end)
    
    -- ⚠️ 3. SENSOR ANTI-KICK & ERROR (Tetap dipertahankan)
    game:GetService("GuiService").ErrorMessageChanged:Connect(function(errMsg)
        local msg = errMsg:lower()
        if msg:find("kick") or msg:find("error") or msg:find("discon") or msg:find("sentinel") then
            pcall(function()
                writefile("arsy_warn_" .. usn .. ".txt", "KICKED: " .. errMsg)
            end)
        end
    end)
end)
