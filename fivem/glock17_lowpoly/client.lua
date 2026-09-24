local WEAPON = `WEAPON_GLOCK17`
local ANIM_DICT = 'anim@w_pi_glock17'

CreateThread(function()
    AddTextEntry('WEAPON_GLOCK17', Config.Label)
end)

if Config.TestCommand then
    RegisterCommand('glock17', function()
        local ped = PlayerPedId()
        GiveWeaponToPed(ped, WEAPON, 17 * 5, false, true)
        GiveWeaponComponentToPed(ped, WEAPON, `COMPONENT_GLOCK17_CLIP_01`)
    end, false)
end

if not Config.ModelClips then
    return
end

local function loadDict()
    RequestAnimDict(ANIM_DICT)
    local timeout = GetGameTimer() + 5000
    while not HasAnimDictLoaded(ANIM_DICT) do
        if GetGameTimer() > timeout then
            return false
        end
        Wait(10)
    end
    return true
end

local function play(entity, clip)
    PlayEntityAnim(entity, clip, ANIM_DICT, 8.0, false, true, false, 0.0, 0)
end

CreateThread(function()
    if not loadDict() then
        print(('[glock17] animation dictionary %s not found'):format(ANIM_DICT))
        return
    end
    local reloading = false
    while true do
        local ped = PlayerPedId()
        if GetSelectedPedWeapon(ped) == WEAPON then
            local entity = GetCurrentPedWeaponEntityIndex(ped)
            if entity ~= 0 then
                local _, ammo = GetAmmoInClip(ped, WEAPON)
                if IsPedShooting(ped) then
                    play(entity, ammo == 0 and 'fire_empty' or 'fire')
                end
                local now = IsPedReloading(ped)
                if now and not reloading then
                    play(entity, ammo == 0 and 'reload_empty' or 'reload')
                end
                reloading = now
            end
            Wait(0)
        else
            reloading = false
            Wait(250)
        end
    end
end)
