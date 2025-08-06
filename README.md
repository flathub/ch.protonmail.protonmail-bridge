# Community build of Proton Mail Bridge

This build is not officially supported by Proton, please report issues at the
package [issue
tracker](https://github.com/flathub/ch.protonmail.protonmail-bridge/issues).

### Autostart

To start automatically on login, create the file `~/.config/autostart/Proton Mail Desktop` with the following contents:

```
[Desktop Entry]
Type=Application
Name=Proton Mail Bridge
Exec=flatpak run ch.protonmail.protonmail-bridge --no-window
X-GNOME-Autostart-enabled=true
```
