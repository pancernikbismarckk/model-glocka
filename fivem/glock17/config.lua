Config = {}

-- Name of the weapon in the game (weapon wheel, HUD, inventories that use
-- the game's labels)
Config.Label = 'Glock 17 Gen4'

-- /glock17 gives the weapon with 5 magazines of ammunition. For testing
-- only: every player could use it, keep it false on a public server.
Config.TestCommand = false

-- In the game the weapon uses the standard pistol animations: they move the
-- slide and the trigger of this model, the empty case is ejected from the
-- ejection port (particle eject_pistol) and the muzzle flash appears at the
-- muzzle.  Setting this to true also plays this model's own clips
-- (stream/anim@w_pi_glock17.ycd: fire, fire_empty, reload, reload_empty),
-- which additionally move the barrel, the slide stop and the magazine
-- catch.  Experimental.
Config.ModelClips = false
