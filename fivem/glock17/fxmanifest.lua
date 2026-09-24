fx_version 'cerulean'
game 'gta5'
lua54 'yes'

name 'glock17'
description 'Glock 17 Gen4 - add-on weapon WEAPON_GLOCK17'
version '1.0.0'

files {
    'meta/weaponcomponents.meta',
    'meta/weaponarchetypes.meta',
    'meta/weaponanimations.meta',
    'meta/pedpersonality.meta',
    'meta/weapons.meta',
}

-- the order matters: components before the weapon that uses them
data_file 'WEAPONCOMPONENTSINFO_FILE' 'meta/weaponcomponents.meta'
data_file 'WEAPON_METADATA_FILE' 'meta/weaponarchetypes.meta'
data_file 'WEAPON_ANIMATIONS_FILE' 'meta/weaponanimations.meta'
data_file 'PED_PERSONALITY_FILE' 'meta/pedpersonality.meta'
data_file 'WEAPONINFO_FILE' 'meta/weapons.meta'

client_scripts {
    'config.lua',
    'client.lua',
}
