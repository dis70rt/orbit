-- Load from hyprland.lua with dofile(os.getenv('HOME') .. '/Projects/Orbit/config/hyprland.lua').
-- Change trigger to e.g. 'SUPER + mouse:274' to preserve unmodified middle click.
-- Change this path if the checkout is elsewhere.
local orbit = os.getenv('HOME') .. '/Projects/Orbit/bin/orbit'
local trigger = 'mouse:274'
hl.on('hyprland.start', function() hl.exec_cmd(orbit .. ' serve') end)
hl.bind(trigger, hl.dsp.exec_cmd(orbit .. ' show'), { description = 'Open Orbit wheel' })
hl.bind(trigger, hl.dsp.exec_cmd(orbit .. ' release'), {
    release = true, ignore_mods = true, description = 'Release Orbit selection'
})

hl.layer_rule({
    name = 'orbit-hud',
    match = { namespace = '^(orbit)$' },
    blur = true,
    ignore_alpha = 0.01,
    no_anim = true,
})
