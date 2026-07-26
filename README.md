# catos-niri-noctaliav5

Complete CatOS Niri desktop Profile powered by Noctalia.

The repository contains the installed Profile tree directly:

```text
usr/share/catdot/profiles/catos-niri-noctaliav5/profile.toml
usr/share/catos-niri-noctaliav5/...
```

Select the Profile with:

```sh
catdot select catos-niri-noctaliav5
```

Catdot installs the exact package names declared by the Profile and maps the
content below `/usr/share/catos-niri-noctaliav5` into the user's HOME. Switching a
Profile does not restart applications or the desktop session.

## Managed configuration

The Profile owns and refreshes these paths:

```text
.config/niri/config.kdl
.gtkrc-2.0
.config/gtk-3.0/settings.ini
.config/gtk-4.0/settings.ini
.config/gtk-4.0/gtk.css
.icons/default/index.theme
```

Run the following command to explicitly accept a newer installed revision:

```sh
catdot update catos-niri-noctaliav5
```

## Seed configuration

All other files under `/usr/share/catos-niri-noctaliav5` are initial Profile seeds.
The managed main Niri config includes noctalia fragments plus the profile-scoped
`~/.config/niri/custom/catos-niri-noctaliav5/` directory. Its `input.kdl`,
`outputs.kdl`, and `rules.kdl` files are seeded once and are never managed, so
later selections and updates preserve user changes. noctalia, noctalia-orientd and
kitty configuration remain seeds as well.

Niri starts Xwayland Satellite, fcitx5 and noctalia directly from `config.kdl`. Terminal and
launcher bindings invoke kitty and noctalia directly; no Catdot runtime wrapper is
used.
