# catos-niri-noctaliav5

Complete CatOS Niri desktop Profile powered by Noctalia v5.

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

The Profile owns and refreshes the distribution-maintained configuration:

```text
.config/niri/config.kdl
.config/niri/noctalia/binds.kdl
.config/niri/noctalia/blur.kdl
.config/niri/noctalia/cursor.kdl
.config/niri/noctalia/layout.kdl
.config/niri/noctalia/wpblur.kdl
.config/kitty/kitty.conf
.config/noctalia/config.toml
.config/xdg-desktop-portal/niri-portals.conf
.gtkrc-2.0
.config/gtk-3.0/settings.ini
.config/gtk-4.0/settings.ini
.config/qt6ct/qt6ct.conf
.icons/default/index.theme
.config/starship.toml
```

Run the following command to explicitly accept a newer installed revision:

```sh
catdot update catos-niri-noctaliav5
```

## Seed configuration

Machine-specific, user-specific, and runtime-generated files are intentionally
left outside `manage` so later Catdot updates cannot overwrite local state.
Important seeds include:

```text
.config/niri/noctalia.kdl
.config/niri/custom/catos-niri-noctaliav5/input.kdl
.config/niri/custom/catos-niri-noctaliav5/outputs.kdl
.config/niri/custom/catos-niri-noctaliav5/rules.kdl
.config/dconf/user
.config/dconf/all.ini
.config/xsettingsd/xsettingsd.conf
```

`noctalia.kdl` is a bootable initial snapshot, but Noctalia's built-in Niri
template rewrites it at runtime. The profile-scoped `custom/` files are seeded
once for machine input, output, and rule customization. The dconf database is
also seeded once so desktop defaults do not replace later user changes.

Niri starts Xwayland Satellite, fcitx5, Noctalia, the polkit agent, and the
portal from `config.kdl`. Terminal and launcher bindings invoke Kitty and
Noctalia directly; no Catdot runtime wrapper is used.
