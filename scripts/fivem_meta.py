"""
FiveM / GTA V metadata of the Glock 17 add-on weapon (no Blender needed).

The weapon uses the values of the game's standard pistol (WEAPON_PISTOL):
handling, damage, sounds, effects (muzzle flash, ejected shell) and the
ped animation sets, so it behaves and animates like a vanilla pistol.
Differences: names, the model, 17 rounds in the magazine and the rail
flashlight attachment point.

metas(...) returns {file name: XML text} for the meta/ folder;
fxmanifest(), client_lua(), config_lua() return the resource scripts.
"""

BASE_FIELDS = [
    "CoverMovementClipSetHash", "CoverMovementExtraClipSetHash",
    "CoverAlternateMovementClipSetHash", "CoverWeaponClipSetHash",
    "MotionClipSetHash", "MotionFilterHash", "MotionCrouchClipSetHash",
    "MotionStrafingClipSetHash", "MotionStrafingStealthClipSetHash",
    "MotionStrafingUpperBodyClipSetHash", "WeaponClipSetHash",
    "WeaponClipSetStreamedHash", "WeaponClipSetHashInjured",
    "WeaponClipSetHashStealth", "WeaponClipSetHashHiCover",
    "AlternativeClipSetWhenBlocked", "ScopeWeaponClipSet",
    "AlternateAimingStandingClipSetHash",
    "AlternateAimingCrouchingClipSetHash",
    "FiringVariationsStandingClipSetHash",
    "FiringVariationsCrouchingClipSetHash", "AimTurnStandingClipSetHash",
    "AimTurnCrouchingClipSetHash", "MeleeClipSetHash",
    "MeleeVariationClipSetHash", "MeleeTauntClipSetHash",
    "MeleeSupportTauntClipSetHash", "MeleeStealthClipSetHash",
    "ShellShockedClipSetHash", "JumpUpperbodyClipSetHash",
    "FallUpperbodyClipSetHash", "FromStrafeTransitionUpperBodyClipSetHash",
    "SwapWeaponFilterHash", "SwapWeaponInLowCoverFilterHash",
    "AnimFireRateModifier", "AnimBlindFireRateModifier",
    "AnimWantingToShootFireRateModifier", "UseFromStrafeUpperBodyAimNetwork",
    "AimingDownTheBarrel", "WeaponSwapData",
    "AimGrenadeThrowNormalClipsetHash", "AimGrenadeThrowAlternateClipsetHash",
]
# (set, fallback, fields with a value, extra fields in order; a leading
# '^' puts the field before the base fields)
ANIM_SETS = [
    ('Default', None, {
        'CoverAlternateMovementClipSetHash': 'cover@move@ai@base@1h',
        'CoverWeaponClipSetHash': 'Cover_Wpn_Pistol',
        'MotionClipSetHash': 'weapons@pistol@pistol',
        'MotionFilterHash': 'BothArms_filter',
        'WeaponClipSetHash': 'weapons@pistol@pistol',
        'WeaponClipSetStreamedHash': 'weapons@pistol@pistol_str',
        'WeaponClipSetHashInjured': 'weapons@pistol@pistol_injured',
        'WeaponClipSetHashStealth': 'weapons@pistol@pistol@stealth',
        'FiringVariationsStandingClipSetHash': 'combat_fire_variations_pistol',
        'AimTurnStandingClipSetHash': 'combat_aim_turns_pistol',
        'MeleeClipSetHash': 'melee@pistol@streamed_core',
        'ShellShockedClipSetHash': 'reaction@shellshock@unarmed',
        'JumpUpperbodyClipSetHash': 'MOVE_JUMP@WEAPONS@PISTOL',
        'FallUpperbodyClipSetHash': 'MOVE_FALL@WEAPONS@PISTOL',
        'FromStrafeTransitionUpperBodyClipSetHash': 'weapons@pistol@',
        'SwapWeaponFilterHash': 'RightArm_NoSpine_filter',
        'SwapWeaponInLowCoverFilterHash': 'RightArm_NoSpine_filter',
        'AnimFireRateModifier': {'value': '1.000000'},
        'AnimBlindFireRateModifier': {'value': '1.000000'},
        'AnimWantingToShootFireRateModifier': {'value': '3.000000'},
        'UseFromStrafeUpperBodyAimNetwork': {'value': 'true'},
        'AimingDownTheBarrel': {'value': 'true'},
        'WeaponSwapData': {'ref': 'SWAP_DEFAULT'},
        'AimGrenadeThrowNormalClipsetHash': 'Wpn_Thrown_Grenade_Aiming_Rifle',
    }, [
    ]),
    ('Gang', 'Default', {
        'FiringVariationsStandingClipSetHash':
            'combat_fire_variations_gang_pistol',
        'FromStrafeTransitionUpperBodyClipSetHash': 'weapons@pistol@',
        'AnimFireRateModifier': {'value': '1.000000'},
        'AnimBlindFireRateModifier': {'value': '1.000000'},
        'AnimWantingToShootFireRateModifier': {'value': '-1.000000'},
        'UseFromStrafeUpperBodyAimNetwork': {'value': 'true'},
        'AimingDownTheBarrel': {'value': 'true'},
        'WeaponSwapData': {'ref': 'NULL'},
    }, [
    ]),
    ('Hillbilly', 'Default', {
        'CoverAlternateMovementClipSetHash': 'cover@move@ai@base@1h',
        'CoverWeaponClipSetHash': 'Cover_Wpn_Pistol',
        'MotionClipSetHash': 'weapons@pistol_1h@hillbilly',
        'MotionFilterHash': 'BothArms_filter',
        'WeaponClipSetHash': 'weapons@pistol_1h@hillbilly',
        'WeaponClipSetStreamedHash': 'weapons@pistol_1h@hillbilly_str',
        'WeaponClipSetHashInjured': 'weapons@pistol@pistol_injured',
        'WeaponClipSetHashStealth': 'weapons@pistol@pistol@stealth',
        'FiringVariationsStandingClipSetHash':
            'combat_fire_variations_hillbilly_pistol_1H',
        'AimTurnStandingClipSetHash': 'combat_aim_turns_pistol',
        'MeleeClipSetHash': 'melee@pistol@streamed_core',
        'ShellShockedClipSetHash': 'reaction@shellshock@unarmed',
        'JumpUpperbodyClipSetHash': 'MOVE_JUMP@WEAPONS@PISTOL',
        'FallUpperbodyClipSetHash': 'MOVE_FALL@WEAPONS@PISTOL',
        'FromStrafeTransitionUpperBodyClipSetHash':
            'weapons@pistol_1h@hillbilly',
        'SwapWeaponFilterHash': 'RightArm_NoSpine_filter',
        'SwapWeaponInLowCoverFilterHash': 'RightArm_NoSpine_filter',
        'AnimFireRateModifier': {'value': '1.000000'},
        'AnimBlindFireRateModifier': {'value': '1.000000'},
        'AnimWantingToShootFireRateModifier': {'value': '3.000000'},
        'UseFromStrafeUpperBodyAimNetwork': {'value': 'true'},
        'AimingDownTheBarrel': {'value': 'true'},
        'WeaponSwapData': {'ref': 'SWAP_DEFAULT'},
        'GestureBeckonOverrideClipSetHash':
            'combat_gestures_beckon_pistol_1h_hillbilly',
        'GestureOverThereOverrideClipSetHash':
            'combat_gestures_overthere_pistol_1h_hillbilly',
        'GestureHaltOverrideClipSetHash':
            'combat_gestures_halt_pistol_1h_hillbilly',
        'GestureGlancesOverrideClipSetHash':
            'combat_gestures_glances_pistol_1h_hillbilly',
        'CombatReactionOverrideClipSetHash':
            'combat_reactions_pistol_1h_hillbilly',
        'UseLeftHandIKAllowTags': {'value': 'true'},
    }, [
        'GestureBeckonOverrideClipSetHash',
        'GestureOverThereOverrideClipSetHash',
        'GestureHaltOverrideClipSetHash',
        'GestureGlancesOverrideClipSetHash',
        'CombatReactionOverrideClipSetHash',
        'UseLeftHandIKAllowTags',
    ]),
    ('Gang1H', 'Gang', {
        'CoverAlternateMovementClipSetHash': 'cover@move@ai@base@1h',
        'CoverWeaponClipSetHash': 'Cover_Wpn_Pistol',
        'MotionClipSetHash': 'weapons@pistol_1h@gang',
        'MotionFilterHash': 'BothArms_filter',
        'WeaponClipSetHash': 'weapons@pistol_1h@gang',
        'WeaponClipSetStreamedHash': 'weapons@pistol_1h@gang_str',
        'WeaponClipSetHashInjured': 'weapons@pistol@pistol_injured',
        'WeaponClipSetHashStealth': 'weapons@pistol@pistol@stealth',
        'FiringVariationsStandingClipSetHash':
            'combat_fire_variations_gang_pistol_1H',
        'AimTurnStandingClipSetHash': 'combat_aim_turns_pistol',
        'MeleeClipSetHash': 'melee@pistol@streamed_core',
        'ShellShockedClipSetHash': 'reaction@shellshock@unarmed',
        'JumpUpperbodyClipSetHash': 'MOVE_JUMP@WEAPONS@PISTOL',
        'FallUpperbodyClipSetHash': 'MOVE_FALL@WEAPONS@PISTOL',
        'FromStrafeTransitionUpperBodyClipSetHash': 'weapons@pistol_1h@gang',
        'SwapWeaponFilterHash': 'RightArm_NoSpine_filter',
        'SwapWeaponInLowCoverFilterHash': 'RightArm_NoSpine_filter',
        'AnimFireRateModifier': {'value': '1.000000'},
        'AnimBlindFireRateModifier': {'value': '1.000000'},
        'AnimWantingToShootFireRateModifier': {'value': '3.000000'},
        'UseFromStrafeUpperBodyAimNetwork': {'value': 'true'},
        'AimingDownTheBarrel': {'value': 'true'},
        'WeaponSwapData': {'ref': 'SWAP_DEFAULT'},
        'GestureBeckonOverrideClipSetHash':
            'combat_gestures_beckon_pistol_1h_gang',
        'GestureOverThereOverrideClipSetHash':
            'combat_gestures_overthere_pistol_1h_gang',
        'GestureHaltOverrideClipSetHash':
            'combat_gestures_halt_pistol_1h_gang',
        'GestureGlancesOverrideClipSetHash':
            'combat_gestures_glances_pistol_1h_gang',
        'CombatReactionOverrideClipSetHash': 'combat_reactions_pistol_1h_gang',
        'UseLeftHandIKAllowTags': {'value': 'true'},
    }, [
        'GestureBeckonOverrideClipSetHash',
        'GestureOverThereOverrideClipSetHash',
        'GestureHaltOverrideClipSetHash',
        'GestureGlancesOverrideClipSetHash',
        'CombatReactionOverrideClipSetHash',
        'UseLeftHandIKAllowTags',
    ]),
    ('FirstPerson', 'Default', {
        'FPSFidgetClipsetHashes': [
            'weapons@first_person@aim_idle@p_m_zero@pistol@shared@fidgets@a',
            'weapons@first_person@aim_idle@p_m_zero@pistol@shared@fidgets@b',
            'weapons@first_person@aim_idle@p_m_zero@pistol@shared@fidgets@c'],
        'MovementOverrideClipSetHash': 'move_m@generic',
        'CoverAlternateMovementClipSetHash': 'cover@move@ai@base@1h',
        'CoverWeaponClipSetHash': 'Cover_FirstPerson_Wpn_Pistol',
        'MotionClipSetHash':
            'weapons@first_person@aim_idle@generic@pistol@shared@core',
        'MotionFilterHash': 'BothArms_filter',
        'MotionStrafingStealthClipSetHash': 'move_ped_strafing_stealth',
        'WeaponClipSetHash':
            'weapons@first_person@aim_idle@generic@pistol@shared@core',
        'WeaponClipSetStreamedHash':
            'weapons@first_person@aim_rng@generic@pistol@pistol_str',
        'WeaponClipSetHashInjured': 'weapons@pistol@pistol_injured',
        'WeaponClipSetHashStealth':
            'weapons@first_person@aim_stealth@generic@pistol@shared@core',
        'FiringVariationsStandingClipSetHash': 'combat_fire_variations_pistol',
        'AimTurnStandingClipSetHash': 'combat_aim_turns_pistol',
        'MeleeClipSetHash': 'melee@pistol@streamed_fps',
        'ShellShockedClipSetHash': 'reaction@shellshock@unarmed',
        'JumpUpperbodyClipSetHash': 'MOVE_JUMP@WEAPONS@PISTOL',
        'FallUpperbodyClipSetHash': 'MOVE_FALL@WEAPONS@PISTOL',
        'FromStrafeTransitionUpperBodyClipSetHash': 'weapons@pistol@',
        'SwapWeaponFilterHash': 'RightArm_NoSpine_filter',
        'SwapWeaponInLowCoverFilterHash': 'RightArm_NoSpine_filter',
        'AnimFireRateModifier': {'value': '1.000000'},
        'AnimBlindFireRateModifier': {'value': '1.000000'},
        'AnimWantingToShootFireRateModifier': {'value': '3.000000'},
        'UseFromStrafeUpperBodyAimNetwork': {'value': 'true'},
        'AimingDownTheBarrel': {'value': 'true'},
        'WeaponSwapData': {'ref': 'SWAP_DEFAULT'},
        'AimGrenadeThrowNormalClipsetHash':
            'weapons@first_person@aim_rng@generic@pistol@shared@core',
        'FPSTransitionFromRNGHash':
            'weapons@first_person@aim_rng@p_m_zero@pistol@shared@aim_trans@rng_to_idle',
        'FPSTransitionFromLTHash':
            'weapons@first_person@aim_lt@p_m_zero@pistol@shared@aim_trans@lt_to_idle',
        'FPSTransitionFromScopeHash':
            'weapons@first_person@aim_scope@p_m_zero@pistol@shared@aim_trans@scope_to_idle',
        'FPSTransitionFromUnholsterHash':
            'weapons@first_person@aim_idle@p_m_zero@pistol@shared@aim_trans@unholster_to_idle',
        'FPSTransitionFromStealthHash':
            'weapons@first_person@aim_stealth@p_m_zero@pistol@shared@aim_trans@stealth_to_idle',
        'FPSTransitionToStealthHash':
            'weapons@first_person@aim_idle@p_m_zero@pistol@shared@aim_trans@idle_to_stealth',
        'FPSTransitionToStealthFromUnholsterHash':
            'weapons@first_person@aim_stealth@p_m_zero@pistol@shared@aim_trans@unholster_to_stealth',
        'WeaponClipSetHashForClone':
            'weapons@first_person@aim_idle@remote_clone@pistol@shared@core',
    }, [
        '^MovementOverrideClipSetHash',
        'FPSTransitionFromIdleHash',
        'FPSTransitionFromRNGHash',
        'FPSTransitionFromLTHash',
        'FPSTransitionFromScopeHash',
        'FPSTransitionFromUnholsterHash',
        'FPSTransitionFromStealthHash',
        'FPSTransitionToStealthHash',
        'FPSTransitionToStealthFromUnholsterHash',
        'FPSFidgetClipsetHashes',
        'WeaponClipSetHashForClone',
    ]),
    ('FirstPersonAiming', 'Default', {
        'FPSFidgetClipsetHashes': [
            'weapons@first_person@aim_lt@p_m_zero@pistol@shared@fidgets@a',
            'weapons@first_person@aim_lt@p_m_zero@pistol@shared@fidgets@b',
            'weapons@first_person@aim_lt@p_m_zero@pistol@shared@fidgets@c',
            'weapons@first_person@aim_lt@p_m_zero@pistol@shared@fidgets@d'],
        'CoverAlternateMovementClipSetHash': 'cover@move@ai@base@1h',
        'CoverWeaponClipSetHash': 'Cover_FirstPerson_Wpn_Pistol',
        'MotionClipSetHash':
            'weapons@first_person@aim_rng@generic@pistol@shared@core',
        'MotionFilterHash': 'BothArms_filter',
        'MotionStrafingStealthClipSetHash': 'move_ped_strafing_stealth',
        'WeaponClipSetHash':
            'weapons@first_person@aim_lt@generic@pistol@w_fire',
        'WeaponClipSetStreamedHash':
            'weapons@first_person@aim_rng@generic@pistol@pistol_str',
        'WeaponClipSetHashInjured': 'weapons@pistol@pistol_injured',
        'WeaponClipSetHashStealth':
            'weapons@first_person@aim_lt@generic@pistol@w_fire',
        'FiringVariationsStandingClipSetHash': 'combat_fire_variations_pistol',
        'AimTurnStandingClipSetHash': 'combat_aim_turns_pistol',
        'MeleeClipSetHash': 'melee@pistol@streamed_fps',
        'ShellShockedClipSetHash': 'reaction@shellshock@unarmed',
        'JumpUpperbodyClipSetHash': 'MOVE_JUMP@WEAPONS@PISTOL',
        'FallUpperbodyClipSetHash': 'MOVE_FALL@WEAPONS@PISTOL',
        'FromStrafeTransitionUpperBodyClipSetHash': 'weapons@pistol@',
        'SwapWeaponFilterHash': 'RightArm_NoSpine_filter',
        'SwapWeaponInLowCoverFilterHash': 'RightArm_NoSpine_filter',
        'AnimFireRateModifier': {'value': '1.000000'},
        'AnimBlindFireRateModifier': {'value': '1.000000'},
        'AnimWantingToShootFireRateModifier': {'value': '3.000000'},
        'UseFromStrafeUpperBodyAimNetwork': {'value': 'true'},
        'AimingDownTheBarrel': {'value': 'true'},
        'WeaponSwapData': {'ref': 'SWAP_DEFAULT'},
        'AimGrenadeThrowNormalClipsetHash':
            'weapons@first_person@aim_rng@generic@pistol@shared@core',
        'FPSTransitionFromIdleHash':
            'weapons@first_person@aim_idle@p_m_zero@pistol@shared@aim_trans@idle_to_lt',
        'FPSTransitionFromRNGHash':
            'weapons@first_person@aim_rng@p_m_zero@pistol@shared@aim_trans@rng_to_lt',
        'FPSTransitionFromScopeHash':
            'weapons@first_person@aim_scope@p_m_zero@pistol@shared@aim_trans@scope_to_lt',
        'FPSTransitionFromUnholsterHash':
            'weapons@first_person@aim_lt@p_m_zero@pistol@shared@aim_trans@unholster_to_lt',
        'FPSTransitionFromStealthHash':
            'weapons@first_person@aim_stealth@p_m_zero@pistol@shared@aim_trans@stealth_to_lt',
        'FPSTransitionToStealthHash':
            'weapons@first_person@aim_lt@p_m_zero@pistol@shared@aim_trans@lt_to_stealth',
    }, [
        'FPSTransitionFromIdleHash',
        'FPSTransitionFromRNGHash',
        'FPSTransitionFromLTHash',
        'FPSTransitionFromScopeHash',
        'FPSTransitionFromUnholsterHash',
        'FPSTransitionFromStealthHash',
        'FPSTransitionToStealthHash',
        'FPSFidgetClipsetHashes',
    ]),
    ('FirstPersonRNG', 'Default', {
        'FPSFidgetClipsetHashes': [
            'weapons@first_person@aim_rng@p_m_zero@pistol@shared@fidgets@a',
            'weapons@first_person@aim_rng@p_m_zero@pistol@shared@fidgets@b',
            'weapons@first_person@aim_rng@p_m_zero@pistol@shared@fidgets@c'],
        'CoverAlternateMovementClipSetHash': 'cover@move@ai@base@1h',
        'CoverWeaponClipSetHash': 'Cover_FirstPerson_Wpn_Pistol',
        'MotionClipSetHash':
            'weapons@first_person@aim_rng@generic@pistol@shared@core',
        'MotionFilterHash': 'BothArms_filter',
        'MotionStrafingStealthClipSetHash': 'move_ped_strafing_stealth',
        'WeaponClipSetHash': 'weapons@first_person@aim_rng@pistol@pistol',
        'WeaponClipSetStreamedHash':
            'weapons@first_person@aim_rng@generic@pistol@pistol_str',
        'WeaponClipSetHashInjured': 'weapons@pistol@pistol_injured',
        'WeaponClipSetHashStealth':
            'weapons@first_person@aim_rng@pistol@pistol',
        'FiringVariationsStandingClipSetHash': 'combat_fire_variations_pistol',
        'AimTurnStandingClipSetHash': 'combat_aim_turns_pistol',
        'MeleeClipSetHash': 'melee@pistol@streamed_fps',
        'ShellShockedClipSetHash': 'reaction@shellshock@unarmed',
        'JumpUpperbodyClipSetHash': 'MOVE_JUMP@WEAPONS@PISTOL',
        'FallUpperbodyClipSetHash': 'MOVE_FALL@WEAPONS@PISTOL',
        'FromStrafeTransitionUpperBodyClipSetHash': 'weapons@pistol@',
        'SwapWeaponFilterHash': 'RightArm_NoSpine_filter',
        'SwapWeaponInLowCoverFilterHash': 'RightArm_NoSpine_filter',
        'AnimFireRateModifier': {'value': '1.000000'},
        'AnimBlindFireRateModifier': {'value': '1.000000'},
        'AnimWantingToShootFireRateModifier': {'value': '3.000000'},
        'UseFromStrafeUpperBodyAimNetwork': {'value': 'true'},
        'AimingDownTheBarrel': {'value': 'true'},
        'WeaponSwapData': {'ref': 'SWAP_DEFAULT'},
        'AimGrenadeThrowNormalClipsetHash':
            'weapons@first_person@aim_rng@generic@pistol@shared@core',
        'FPSTransitionFromIdleHash':
            'weapons@first_person@aim_idle@p_m_zero@pistol@shared@aim_trans@idle_to_rng',
        'FPSTransitionFromLTHash':
            'weapons@first_person@aim_lt@p_m_zero@pistol@shared@aim_trans@lt_to_rng',
        'FPSTransitionFromScopeHash':
            'weapons@first_person@aim_scope@p_m_zero@pistol@shared@aim_trans@scope_to_rng',
        'FPSTransitionFromUnholsterHash':
            'weapons@first_person@aim_rng@p_m_zero@pistol@shared@aim_trans@unholster_to_rng',
        'FPSTransitionFromStealthHash':
            'weapons@first_person@aim_stealth@p_m_zero@pistol@shared@aim_trans@stealth_to_rng',
        'FPSTransitionToStealthHash':
            'weapons@first_person@aim_rng@p_m_zero@pistol@shared@aim_trans@rng_to_stealth',
    }, [
        'FPSTransitionFromIdleHash',
        'FPSTransitionFromRNGHash',
        'FPSTransitionFromLTHash',
        'FPSTransitionFromScopeHash',
        'FPSTransitionFromUnholsterHash',
        'FPSTransitionFromStealthHash',
        'FPSTransitionToStealthHash',
        'FPSFidgetClipsetHashes',
    ]),
    ('FirstPersonScope', 'Default', {
        'CoverAlternateMovementClipSetHash': 'cover@move@ai@base@1h',
        'CoverWeaponClipSetHash': 'Cover_FirstPerson_Wpn_Pistol',
        'MotionClipSetHash':
            'weapons@first_person@aim_rng@generic@pistol@shared@core',
        'MotionFilterHash': 'BothArms_filter',
        'MotionStrafingStealthClipSetHash': 'move_ped_strafing_stealth',
        'WeaponClipSetHash':
            'weapons@first_person@aim_scope@generic@pistol@w_fire',
        'WeaponClipSetStreamedHash':
            'weapons@first_person@aim_rng@generic@pistol@pistol_str',
        'WeaponClipSetHashInjured': 'weapons@pistol@pistol_injured',
        'WeaponClipSetHashStealth':
            'weapons@first_person@aim_scope@generic@pistol@w_fire',
        'FiringVariationsStandingClipSetHash': 'combat_fire_variations_pistol',
        'AimTurnStandingClipSetHash': 'combat_aim_turns_pistol',
        'MeleeClipSetHash': 'melee@pistol@streamed_fps',
        'ShellShockedClipSetHash': 'reaction@shellshock@unarmed',
        'JumpUpperbodyClipSetHash': 'MOVE_JUMP@WEAPONS@PISTOL',
        'FallUpperbodyClipSetHash': 'MOVE_FALL@WEAPONS@PISTOL',
        'FromStrafeTransitionUpperBodyClipSetHash': 'weapons@pistol@',
        'SwapWeaponFilterHash': 'RightArm_NoSpine_filter',
        'SwapWeaponInLowCoverFilterHash': 'RightArm_NoSpine_filter',
        'AnimFireRateModifier': {'value': '1.000000'},
        'AnimBlindFireRateModifier': {'value': '1.000000'},
        'AnimWantingToShootFireRateModifier': {'value': '3.000000'},
        'UseFromStrafeUpperBodyAimNetwork': {'value': 'true'},
        'AimingDownTheBarrel': {'value': 'true'},
        'WeaponSwapData': {'ref': 'SWAP_DEFAULT'},
        'AimGrenadeThrowNormalClipsetHash':
            'weapons@first_person@aim_rng@generic@pistol@shared@core',
        'FPSTransitionFromIdleHash':
            'weapons@first_person@aim_idle@p_m_zero@pistol@shared@aim_trans@idle_to_scope',
        'FPSTransitionFromRNGHash':
            'weapons@first_person@aim_rng@p_m_zero@pistol@shared@aim_trans@rng_to_scope',
        'FPSTransitionFromLTHash':
            'weapons@first_person@aim_lt@p_m_zero@pistol@shared@aim_trans@lt_to_scope',
        'FPSTransitionFromUnholsterHash':
            'weapons@first_person@aim_scope@p_m_zero@pistol@shared@aim_trans@unholster_to_scope',
        'FPSTransitionFromStealthHash':
            'weapons@first_person@aim_stealth@p_m_zero@pistol@shared@aim_trans@stealth_to_scope',
        'FPSTransitionToStealthHash':
            'weapons@first_person@aim_scope@p_m_zero@pistol@shared@aim_trans@scope_to_stealth',
    }, [
        'FPSTransitionFromIdleHash',
        'FPSTransitionFromRNGHash',
        'FPSTransitionFromLTHash',
        'FPSTransitionFromScopeHash',
        'FPSTransitionFromUnholsterHash',
        'FPSTransitionFromStealthHash',
        'FPSTransitionToStealthHash',
    ]),
]

UNHOLSTER = [
    ("UNHOLSTER_UNARMED", "unarmed_holster_1h"),
    ("UNHOLSTER_2H_MELEE", "2h_melee_holster_1h"),
    ("UNHOLSTER_1H", "1h_holster_1h"),
    ("UNHOLSTER_2H", "2h_holster_1h"),
    ("UNHOLSTER_MINIGUN", "mini_holster_1h"),
    ("UNHOLSTER_UNARMED_STEALTH", "unarmed_holster_1h"),
    ("UNHOLSTER_2H_MELEE_STEALTH", "unarmed_holster_1h"),
    ("UNHOLSTER_1H_STEALTH", "1h_holster_1h"),
    ("UNHOLSTER_2H_STEALTH", "2h_holster_1h"),
]
# movement mode -> (ped clip set suffix, action transition, stealth
# transition, left hand IK)
MOVEMENT_MODES = [
    ("DEFAULT_ACTION", "P_M_ZERO", "MOVE_ACTION@GENERIC@TRANS@1H",
     "MOVE_STEALTH@GENERIC@TRANS@1H", True),
    ("MP_FEMALE_ACTION", "P_M_ZERO", "MOVE_ACTION@MP_FEMALE@ARMED@1H@TRANS",
     "MOVE_STEALTH@MP_FEMALE@1H@TRANS", True),
    ("MICHAEL_ACTION", "P_M_ZERO", "MOVE_ACTION@P_M_ZERO@ARMED@1H@TRANS@A",
     "MOVE_STEALTH@P_M_ZERO@1H@TRANS@A", True),
    ("FRANKLIN_ACTION", "P_M_ONE", "MOVE_ACTION@P_M_ONE@ARMED@1H@TRANS@A",
     "MOVE_STEALTH@P_M_ONE@1H@TRANS@A", False),
    ("TREVOR_ACTION", "P_M_TWO", "MOVE_ACTION@P_M_TWO@ARMED@1H@TRANS@A",
     "MOVE_STEALTH@P_M_TWO@1H@TRANS@A", False),
]


def _field(tag, value, indent):
    pad = "\t" * indent
    if isinstance(value, list):
        items = "".join(f"\n{pad}\t<Item>{v}</Item>" for v in value)
        return f"{pad}<{tag}>{items}\n{pad}</{tag}>"
    if isinstance(value, dict):
        attrs = " ".join(f'{k}="{v}"' for k, v in value.items())
        return f"{pad}<{tag} {attrs}/>"
    if value:
        return f"{pad}<{tag}>{value}</{tag}>"
    return f"{pad}<{tag}/>"


def weapon_animations_meta(weapon):
    out = ["<CWeaponAnimationsSets>", "\t<WeaponAnimationsSets>"]
    for key, fallback, values, extra in ANIM_SETS:
        out.append(f'\t\t<Item key="{key}">')
        if fallback:
            out.append(f"\t\t\t<Fallback>{fallback}</Fallback>")
        out.append("\t\t\t<WeaponAnimations>")
        out.append(f'\t\t\t\t<Item key="{weapon}">')
        first = [e[1:] for e in extra if e.startswith("^")]
        last = [e for e in extra if not e.startswith("^")]
        for tag in first + BASE_FIELDS + last:
            out.append(_field(tag, values.get(tag, ""), 5))
        out += ["\t\t\t\t</Item>", "\t\t\t</WeaponAnimations>", "\t\t</Item>"]
    out += ["\t</WeaponAnimationsSets>", "</CWeaponAnimationsSets>", ""]
    return "\n".join(out)


def ped_personality_meta(weapon):
    out = ["<CPedModelInfo__PersonalityDataList>", "\t<MovementModeUnholsterData>"]
    for name, clip in UNHOLSTER:
        out += ["\t\t<Item>", f"\t\t\t<Name>{name}</Name>", "\t\t\t<UnholsterClips>",
                "\t\t\t\t<Item>", "\t\t\t\t\t<Weapons>",
                f"\t\t\t\t\t\t<Item>{weapon}</Item>", "\t\t\t\t\t</Weapons>",
                f"\t\t\t\t\t<Clip>{clip}</Clip>", "\t\t\t\t</Item>",
                "\t\t\t</UnholsterClips>", "\t\t</Item>"]
    out += ["\t</MovementModeUnholsterData>", "\t<MovementModes>"]
    for name, ped, trans_action, trans_stealth, left_ik in MOVEMENT_MODES:
        ik = "true" if left_ik else "false"
        out += ["\t\t<Item>", f"\t\t\t<Name>{name}</Name>", "\t\t\t<MovementModes>"]
        for kind, trans in (("ACTION", trans_action), ("STEALTH", trans_stealth)):
            core = (f"MOVE_ACTION@{ped}@ARMED@CORE" if kind == "ACTION"
                    else f"MOVE_STEALTH@{ped}@UNARMED@CORE")
            upper = (f"MOVE_ACTION@{ped}@ARMED@1H@UPPER" if kind == "ACTION"
                     else f"MOVE_STEALTH@{ped}@1H@UPPER")
            unholster = "UNHOLSTER_1H" if kind == "ACTION" else "UNHOLSTER_1H_STEALTH"
            out += [
                "\t\t\t\t<Item>", "\t\t\t\t\t<Item>", "\t\t\t\t\t\t<Weapons>",
                f"\t\t\t\t\t\t\t<Item>{weapon}</Item>", "\t\t\t\t\t\t</Weapons>",
                "\t\t\t\t\t\t<ClipSets>", "\t\t\t\t\t\t\t<Item>",
                f"\t\t\t\t\t\t\t\t<MovementClipSetId>{core}</MovementClipSetId>",
                f"\t\t\t\t\t\t\t\t<WeaponClipSetId>{upper}</WeaponClipSetId>",
                "\t\t\t\t\t\t\t\t<WeaponClipFilterId>UpperbodyAndIk_filter</WeaponClipFilterId>",
                '\t\t\t\t\t\t\t\t<UpperBodyShadowExpressionEnabled value="true"/>',
                '\t\t\t\t\t\t\t\t<UpperBodyFeatheredLeanEnabled value="true"/>',
                '\t\t\t\t\t\t\t\t<UseWeaponAnimsForGrip value="false"/>',
                f'\t\t\t\t\t\t\t\t<UseLeftHandIk value="{ik}"/>',
                '\t\t\t\t\t\t\t\t<IdleTransitionBlendOutTime value="0.50000000"/>',
                "\t\t\t\t\t\t\t\t<IdleTransitions>",
                f"\t\t\t\t\t\t\t\t\t<Item>{trans}</Item>",
                "\t\t\t\t\t\t\t\t</IdleTransitions>",
                f"\t\t\t\t\t\t\t\t<UnholsterClipSetId>MOVE_{kind}@{ped}@HOLSTER"
                "</UnholsterClipSetId>",
                f"\t\t\t\t\t\t\t\t<UnholsterClipData>{unholster}</UnholsterClipData>",
                "\t\t\t\t\t\t\t</Item>", "\t\t\t\t\t\t</ClipSets>",
                "\t\t\t\t\t</Item>", "\t\t\t\t</Item>"]
        out += ["\t\t\t</MovementModes>",
                '\t\t\t<LastBattleEventHighEnergyStartTime value="0.00000000"/>',
                '\t\t\t<LastBattleEventHighEnergyEndTime value="5.00000000"/>',
                "\t\t</Item>"]
    out += ["\t</MovementModes>", "</CPedModelInfo__PersonalityDataList>", ""]
    return "\n".join(out)


def weapon_archetypes_meta(model, mag_model):
    return f"""<CWeaponModelInfo__InitDataList>
	<InitDatas>
		<Item>
			<modelName>{mag_model}</modelName>
			<txdName>{mag_model}</txdName>
			<ptfxAssetName>NULL</ptfxAssetName>
			<lodDist value="300"/>
		</Item>
		<Item>
			<modelName>{model}</modelName>
			<txdName>{model}</txdName>
			<ptfxAssetName>NULL</ptfxAssetName>
			<lodDist value="500"/>
		</Item>
	</InitDatas>
</CWeaponModelInfo__InitDataList>
"""


def weapon_components_meta(clip_component, mag_model, clip_size):
    return f"""<CWeaponComponentInfoBlob>
	<Infos>
		<Item type="CWeaponComponentClipInfo">
			<Name>{clip_component}</Name>
			<Model>{mag_model}</Model>
			<LocName>WCT_CLIP1</LocName>
			<LocDesc>WCD_P_CLIP1</LocDesc>
			<AttachBone>AAPClip</AttachBone>
			<WeaponAttachBone>WAPClip</WeaponAttachBone>
			<AccuracyModifier type="NULL"/>
			<DamageModifier type="NULL"/>
			<bShownOnWheel value="false"/>
			<CreateObject value="true"/>
			<HudDamage value="0"/>
			<HudSpeed value="0"/>
			<HudCapacity value="0"/>
			<HudAccuracy value="0"/>
			<HudRange value="0"/>
			<ClipSize value="{clip_size}"/>
			<AmmoInfo/>
			<ReloadData ref="RELOAD_DEFAULT_WITH_EMPTIES"/>
		</Item>
	</Infos>
	<InfoBlobName/>
</CWeaponComponentInfoBlob>
"""


def weapons_meta(weapon, model, clip_component, clip_size, slot):
    return f"""<CWeaponInfoBlob>
	<SlotNavigateOrder>
		<Item>
			<WeaponSlots>
				<Item>
					<OrderNumber value="409"/>
					<Entry>{slot}</Entry>
				</Item>
			</WeaponSlots>
		</Item>
	</SlotNavigateOrder>
	<Infos>
		<Item>
			<Infos>
				<Item type="CWeaponInfo">
					<Name>{weapon}</Name>
					<Model>{model}</Model>
					<Audio>AUDIO_ITEM_PISTOL</Audio>
					<Slot>{slot}</Slot>
					<DamageType>BULLET</DamageType>
					<Explosion>
						<Default>DONTCARE</Default>
						<HitCar>DONTCARE</HitCar>
						<HitTruck>DONTCARE</HitTruck>
						<HitBike>DONTCARE</HitBike>
						<HitBoat>DONTCARE</HitBoat>
						<HitPlane>DONTCARE</HitPlane>
					</Explosion>
					<FireType>INSTANT_HIT</FireType>
					<WheelSlot>WHEEL_PISTOL</WheelSlot>
					<Group>GROUP_PISTOL</Group>
					<AmmoInfo ref="AMMO_PISTOL"/>
					<AimingInfo ref="PISTOL_2H_BASE_STRAFE"/>
					<ClipSize value="{clip_size}"/>
					<AccuracySpread value="1.500000"/>
					<AccurateModeAccuracyModifier value="0.500000"/>
					<RunAndGunAccuracyModifier value="2.000000"/>
					<RunAndGunAccuracyMaxModifier value="1.000000"/>
					<RecoilAccuracyMax value="1.000000"/>
					<RecoilErrorTime value="3.300000"/>
					<RecoilRecoveryRate value="1.000000"/>
					<RecoilAccuracyToAllowHeadShotAI value="1000.000000"/>
					<MinHeadShotDistanceAI value="1000.000000"/>
					<MaxHeadShotDistanceAI value="1000.000000"/>
					<HeadShotDamageModifierAI value="1000.000000"/>
					<RecoilAccuracyToAllowHeadShotPlayer value="0.175000"/>
					<MinHeadShotDistancePlayer value="5.000000"/>
					<MaxHeadShotDistancePlayer value="40.000000"/>
					<HeadShotDamageModifierPlayer value="20.000000"/>
					<Damage value="26.000000"/>
					<DamageTime value="0.000000"/>
					<DamageTimeInVehicle value="0.000000"/>
					<DamageTimeInVehicleHeadShot value="0.000000"/>
					<HitLimbsDamageModifier value="0.500000"/>
					<NetworkHitLimbsDamageModifier value="0.800000"/>
					<LightlyArmouredDamageModifier value="0.750000"/>
					<Force value="50.000000"/>
					<ForceHitPed value="125.000000"/>
					<ForceHitVehicle value="750.000000"/>
					<ForceHitFlyingHeli value="750.000000"/>
					<OverrideForces>
						<Item>
							<BoneTag>BONETAG_HEAD</BoneTag>
							<ForceFront value="100.000000"/>
							<ForceBack value="80.000000"/>
						</Item>
						<Item>
							<BoneTag>BONETAG_NECK</BoneTag>
							<ForceFront value="60.000000"/>
							<ForceBack value="70.000000"/>
						</Item>
						<Item>
							<BoneTag>BONETAG_L_THIGH</BoneTag>
							<ForceFront value="40.000000"/>
							<ForceBack value="1.000000"/>
						</Item>
						<Item>
							<BoneTag>BONETAG_R_THIGH</BoneTag>
							<ForceFront value="40.000000"/>
							<ForceBack value="1.000000"/>
						</Item>
						<Item>
							<BoneTag>BONETAG_L_CALF</BoneTag>
							<ForceFront value="70.000000"/>
							<ForceBack value="80.000000"/>
						</Item>
						<Item>
							<BoneTag>BONETAG_R_CALF</BoneTag>
							<ForceFront value="60.000000"/>
							<ForceBack value="100.000000"/>
						</Item>
					</OverrideForces>
					<ForceMaxStrengthMult value="1.000000"/>
					<ForceFalloffRangeStart value="0.000000"/>
					<ForceFalloffRangeEnd value="50.000000"/>
					<ForceFalloffMin value="1.000000"/>
					<ProjectileForce value="0.000000"/>
					<FragImpulse value="250.000000"/>
					<Penetration value="0.010000"/>
					<VerticalLaunchAdjustment value="0.000000"/>
					<DropForwardVelocity value="0.000000"/>
					<Speed value="2000.000000"/>
					<BulletsInBatch value="1"/>
					<BatchSpread value="0.000000"/>
					<ReloadTimeMP value="-1.000000"/>
					<ReloadTimeSP value="-1.000000"/>
					<VehicleReloadTime value="1.000000"/>
					<AnimReloadRate value="1.000000"/>
					<BulletsPerAnimLoop value="1"/>
					<TimeBetweenShots value="0.370000"/>
					<TimeLeftBetweenShotsWhereShouldFireIsCached value="0.250000"/>
					<SpinUpTime value="0.000000"/>
					<SpinTime value="0.000000"/>
					<SpinDownTime value="0.000000"/>
					<AlternateWaitTime value="-1.000000"/>
					<BulletBendingNearRadius value="0.000000"/>
					<BulletBendingFarRadius value="0.750000"/>
					<BulletBendingZoomedRadius value="0.375000"/>
					<FirstPersonBulletBendingNearRadius value="0.000000"/>
					<FirstPersonBulletBendingFarRadius value="0.750000"/>
					<FirstPersonBulletBendingZoomedRadius value="0.375000"/>
					<Fx>
						<EffectGroup>WEAPON_EFFECT_GROUP_PISTOL_SMALL</EffectGroup>
						<FlashFx>muz_pistol</FlashFx>
						<FlashFxAlt/>
						<FlashFxFP>muz_pistol_fp</FlashFxFP>
						<FlashFxAltFP/>
						<MuzzleSmokeFx>muz_smoking_barrel</MuzzleSmokeFx>
						<MuzzleSmokeFxFP>muz_smoking_barrel_fp</MuzzleSmokeFxFP>
						<MuzzleSmokeFxMinLevel value="0.300000"/>
						<MuzzleSmokeFxIncPerShot value="0.100000"/>
						<MuzzleSmokeFxDecPerSec value="0.275000"/>
						<ShellFx>eject_pistol</ShellFx>
						<ShellFxFP>eject_pistol_fp</ShellFxFP>
						<TracerFx>bullet_tracer</TracerFx>
						<PedDamageHash>BulletSmall</PedDamageHash>
						<TracerFxChanceSP value="0.200000"/>
						<TracerFxChanceMP value="0.750000"/>
						<FlashFxChanceSP value="1.000000"/>
						<FlashFxChanceMP value="1.000000"/>
						<FlashFxAltChance value="0.000000"/>
						<FlashFxScale value="0.800000"/>
						<FlashFxLightEnabled value="true"/>
						<FlashFxLightCastsShadows value="false"/>
						<FlashFxLightOffsetDist value="0.000000"/>
						<FlashFxLightRGBAMin x="255.000000" y="93.000000" z="25.000000"/>
						<FlashFxLightRGBAMax x="255.000000" y="100.000000" z="50.000000"/>
						<FlashFxLightIntensityMinMax x="1.000000" y="2.000000"/>
						<FlashFxLightRangeMinMax x="2.000000" y="2.500000"/>
						<FlashFxLightFalloffMinMax x="1024.000000" y="1536.000000"/>
						<GroundDisturbFxEnabled value="false"/>
						<GroundDisturbFxDist value="5.000000"/>
						<GroundDisturbFxNameDefault/>
						<GroundDisturbFxNameSand/>
						<GroundDisturbFxNameDirt/>
						<GroundDisturbFxNameWater/>
						<GroundDisturbFxNameFoliage/>
					</Fx>
					<InitialRumbleDuration value="150"/>
					<InitialRumbleIntensity value="0.200000"/>
					<InitialRumbleIntensityTrigger value="0.850000"/>
					<RumbleDuration value="95"/>
					<RumbleIntensity value="0.200000"/>
					<RumbleIntensityTrigger value="0.800000"/>
					<RumbleDamageIntensity value="1.000000"/>
					<InitialRumbleDurationFps value="150"/>
					<InitialRumbleIntensityFps value="1.000000"/>
					<RumbleDurationFps value="95"/>
					<RumbleIntensityFps value="1.000000"/>
					<NetworkPlayerDamageModifier value="1.000000"/>
					<NetworkPedDamageModifier value="1.000000"/>
					<NetworkHeadShotPlayerDamageModifier value="2.000000"/>
					<LockOnRange value="55.000000"/>
					<WeaponRange value="120.000000"/>
					<BulletDirectionOffsetInDegrees value="0.000000"/>
					<AiSoundRange value="-1.000000"/>
					<AiPotentialBlastEventRange value="-1.000000"/>
					<DamageFallOffRangeMin value="40.000000"/>
					<DamageFallOffRangeMax value="120.000000"/>
					<DamageFallOffModifier value="0.300000"/>
					<VehicleWeaponHash/>
					<DefaultCameraHash>DEFAULT_THIRD_PERSON_PED_AIM_CAMERA</DefaultCameraHash>
					<CoverCameraHash>DEFAULT_THIRD_PERSON_PED_AIM_IN_COVER_CAMERA</CoverCameraHash>
					<CoverReadyToFireCameraHash/>
					<RunAndGunCameraHash>DEFAULT_THIRD_PERSON_PED_RUN_AND_GUN_CAMERA</RunAndGunCameraHash>
					<CinematicShootingCameraHash>DEFAULT_THIRD_PERSON_PED_CINEMATIC_SHOOTING_CAMERA</CinematicShootingCameraHash>
					<AlternativeOrScopedCameraHash/>
					<RunAndGunAlternativeOrScopedCameraHash/>
					<CinematicShootingAlternativeOrScopedCameraHash/>
					<CameraFov value="45.000000"/>
					<FirstPersonScopeFov value="30.00000"/>
					<FirstPersonRNGOffset x="0.000000" y="0.000000" z="0.000000"/>
					<FirstPersonRNGRotationOffset x="0.000000" y="0.000000" z="0.000000"/>
					<FirstPersonLTOffset x="0.000000" y="0.000000" z="0.000000"/>
					<FirstPersonLTRotationOffset x="0.000000" y="0.000000" z="0.000000"/>
					<FirstPersonScopeOffset x="0.00000" y="0.0000" z="0.0010"/>
					<FirstPersonScopeAttachmentOffset x="0.00000" y="0.0000" z="0.0000"/>
					<FirstPersonScopeRotationOffset x="-0.30000" y="0.0000" z="0.0000"/>
					<FirstPersonScopeAttachmentRotationOffset x="0.00000" y="0.0000" z="0.0000"/>
					<FirstPersonAsThirdPersonIdleOffset x="0.075" y="0.000000" z="0.000000"/>
					<FirstPersonAsThirdPersonRNGOffset x="-0.025" y="-0.025" z="-0.040"/>
					<FirstPersonAsThirdPersonLTOffset x="0.050" y="0.060" z="-0.0250"/>
					<FirstPersonAsThirdPersonScopeOffset x="0.070" y="0.000000" z="-0.020"/>
					<FirstPersonAsThirdPersonWeaponBlockedOffset x="0.000000" y="0.000000" z="0.000000"/>
					<FirstPersonDofSubjectMagnificationPowerFactorNear value="1.025000"/>
					<FirstPersonDofMaxNearInFocusDistance value="0.000000"/>
					<FirstPersonDofMaxNearInFocusDistanceBlendLevel value="0.300000"/>
					<ZoomFactorForAccurateMode value="1.300000"/>
					<RecoilShakeHash>PISTOL_RECOIL_SHAKE</RecoilShakeHash>
					<RecoilShakeHashFirstPerson>FPS_PISTOL_RECOIL_SHAKE</RecoilShakeHashFirstPerson>
					<AccuracyOffsetShakeHash/>
					<MinTimeBetweenRecoilShakes value="150"/>
					<RecoilShakeAmplitude value="1.000000"/>
					<ExplosionShakeAmplitude value="-1.000000"/>
					<IkRecoilDisplacement value="0.01"/>
					<IkRecoilDisplacementScope value="0.005"/>
					<IkRecoilDisplacementScaleBackward value="1.0"/>
					<IkRecoilDisplacementScaleVertical value="0.4"/>
					<ReticuleHudPosition x="0.000000" y="0.000000"/>
					<AimOffsetMin x="0.200000" y="0.100000" z="0.600000"/>
					<AimProbeLengthMin value="0.300000"/>
					<AimOffsetMax x="0.175000" y="-0.200000" z="0.500000"/>
					<AimProbeLengthMax value="0.275000"/>
					<AimOffsetMinFPSIdle x="0.178000" y="0.392000" z="0.135000"/>
					<AimOffsetMedFPSIdle x="0.169000" y="0.312000" z="0.420000"/>
					<AimOffsetMaxFPSIdle x="0.187000" y="0.064000" z="0.649000"/>
					<AimOffsetMinFPSLT x="0.009000" y="0.334000" z="0.555000"/>
					<AimOffsetMaxFPSLT x="0.062000" y="-0.164000" z="0.588000"/>
					<AimOffsetMinFPSRNG x="0.114000" y="0.390000" z="0.485000"/>
					<AimOffsetMaxFPSRNG x="0.113000" y="-0.263000" z="0.586000"/>
					<AimOffsetMinFPSScope x="0.009000" y="0.421000" z="0.462000"/>
					<AimOffsetMaxFPSScope x="0.037000" y="-0.224000" z="0.639000"/>
					<AimOffsetEndPosMinFPSIdle x="0.208000" y="0.700000" z="0.003000"/>
					<AimOffsetEndPosMedFPSIdle x="0.203000" y="0.604000" z="0.553000"/>
					<AimOffsetEndPosMaxFPSIdle x="0.207000" y="-0.040000" z="0.942000"/>
					<TorsoAimOffset x="-1.300000" y="0.550000"/>
					<TorsoCrouchedAimOffset x="0.200000" y="0.050000"/>
					<LeftHandIkOffset x="0.000000" y="0.000000" z="0.000000"/>
					<ReticuleMinSizeStanding value="0.650000"/>
					<ReticuleMinSizeCrouched value="0.550000"/>
					<ReticuleScale value="0.300000"/>
					<ReticuleStyleHash>WEAPON_PISTOL</ReticuleStyleHash>
					<FirstPersonReticuleStyleHash/>
					<PickupHash>PICKUP_WEAPON_PISTOL</PickupHash>
					<MPPickupHash>PICKUP_AMMO_BULLET_MP</MPPickupHash>
					<HumanNameHash>{weapon}</HumanNameHash>
					<MovementModeConditionalIdle>MMI_1Handed</MovementModeConditionalIdle>
					<StatName>PISTOL</StatName>
					<KnockdownCount value="3"/>
					<KillshotImpulseScale value="1.000000"/>
					<NmShotTuningSet>Normal</NmShotTuningSet>
					<AttachPoints>
						<Item>
							<AttachBone>WAPClip</AttachBone>
							<Components>
								<Item>
									<Default value="true"/>
									<Name>{clip_component}</Name>
								</Item>
							</Components>
						</Item>
						<Item>
							<AttachBone>WAPFlshLasr</AttachBone>
							<Components>
								<Item>
									<Default value="false"/>
									<Name>COMPONENT_AT_PI_FLSH</Name>
								</Item>
							</Components>
						</Item>
					</AttachPoints>
					<GunFeedBone/>
					<TargetSequenceGroup>PISTOL</TargetSequenceGroup>
					<WeaponFlags>CarriedInHand Gun CanLockonOnFoot CanLockonInVehicle CanFreeAim AnimReload AnimCrouchFire UsableOnFoot UsableClimbing UsableInCover AllowCloseQuarterKills HasLowCoverReloads HasLowCoverSwaps QuitTransitionToIdleIntroOnWeaponChange DisableLeftHandIkWhenOnFoot TorsoIKForWeaponBlock UseFPSAimIK UseFPSSecondaryMotion</WeaponFlags>
					<TintSpecValues ref="TINT_DEFAULT"/>
					<FiringPatternAliases ref="FIRING_PATTERN_PISTOL"/>
					<ReloadUpperBodyFixupExpressionData ref="default"/>
					<AmmoDiminishingRate value="3"/>
					<AimingBreathingAdditiveWeight value="1.000000"/>
					<FiringBreathingAdditiveWeight value="1.000000"/>
					<StealthAimingBreathingAdditiveWeight value="1.000000"/>
					<StealthFiringBreathingAdditiveWeight value="1.000000"/>
					<AimingLeanAdditiveWeight value="1.000000"/>
					<FiringLeanAdditiveWeight value="1.000000"/>
					<StealthAimingLeanAdditiveWeight value="1.000000"/>
					<StealthFiringLeanAdditiveWeight value="1.000000"/>
					<ExpandPedCapsuleRadius value="0.000000"/>
					<AudioCollisionHash/>
					<HudDamage value="26"/>
					<HudSpeed value="40"/>
					<HudCapacity value="20"/>
					<HudAccuracy value="40"/>
					<HudRange value="25"/>
				</Item>
			</Infos>
		</Item>
	</Infos>
	<Name>{weapon}</Name>
</CWeaponInfoBlob>
"""


def metas(weapon, model, mag_model, clip_component, clip_size):
    slot = "SLOT_" + weapon
    return {
        "weaponcomponents.meta": weapon_components_meta(clip_component, mag_model,
                                                        clip_size),
        "weaponarchetypes.meta": weapon_archetypes_meta(model, mag_model),
        "weaponanimations.meta": weapon_animations_meta(weapon),
        "pedpersonality.meta": ped_personality_meta(weapon),
        "weapons.meta": weapons_meta(weapon, model, clip_component, clip_size,
                                     slot),
    }


META_FILES = ["weaponcomponents.meta", "weaponarchetypes.meta",
              "weaponanimations.meta", "pedpersonality.meta", "weapons.meta"]
DATA_FILES = {
    "weaponcomponents.meta": "WEAPONCOMPONENTSINFO_FILE",
    "weaponarchetypes.meta": "WEAPON_METADATA_FILE",
    "weaponanimations.meta": "WEAPON_ANIMATIONS_FILE",
    "pedpersonality.meta": "PED_PERSONALITY_FILE",
    "weapons.meta": "WEAPONINFO_FILE",
}


def fxmanifest(weapon, description):
    files = "\n".join(f"    'meta/{f}'," for f in META_FILES)
    data = "\n".join(f"data_file '{DATA_FILES[f]}' 'meta/{f}'" for f in META_FILES)
    return f"""fx_version 'cerulean'
game 'gta5'
lua54 'yes'

name '{weapon.lower().replace("weapon_", "")}'
description '{description}'
version '1.0.0'

files {{
{files}
}}

-- the order matters: components before the weapon that uses them
{data}

client_scripts {{
    'config.lua',
    'client.lua',
}}
"""


def config_lua(label):
    return f"""Config = {{}}

-- Name of the weapon in the game (weapon wheel, HUD, inventories that use
-- the game's labels)
Config.Label = '{label}'

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
"""


def client_lua(weapon, clip_component, anim_dict, clip_size):
    return f"""local WEAPON = `{weapon}`
local ANIM_DICT = '{anim_dict}'

CreateThread(function()
    AddTextEntry('{weapon}', Config.Label)
end)

if Config.TestCommand then
    RegisterCommand('glock17', function()
        local ped = PlayerPedId()
        GiveWeaponToPed(ped, WEAPON, {clip_size} * 5, false, true)
        GiveWeaponComponentToPed(ped, WEAPON, `{clip_component}`)
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
"""
