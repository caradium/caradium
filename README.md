# Caradium Add-ons Repository

The Caradium Add-ons repository is a collection of add-ons for [CoreELEC](https://coreelec.org/). They may work with similar forks like [LibreELEC](https://libreelec.tv/) but are unlikely to have been tested.

## Disclaimers

### Keep it legal and carry on

Responsibility for the installation, the configuration and the operation of add-ons of the Caradium Add-ons repository, and for the consequences thereof, lies exclusively with the user.

### System Resources

CoreELEC runs on many hardware, some of which have just enough resources for Kodi. Add-ons of the Caradium Add-ons repository will compete with Kodi for these resources, especially if they are limited. Therefore, consider using appropriate hardware or limiting the number of installed add-ons.

### Support

The add-ons are built with the CoreELEC build system to run on the CoreELEC operating system. The Carardium Add-ons repository is however not otherwise related to the CoreELEC project. Do therefore not expect any support from the CoreELEC project with add-ons of the Caradium Add-ons repository.

## Installation

The Caradium Addons repository needs to be installed from a zip file.

Download the [latest release from here](https://github.com/caradium/caradium/releases/latest/download/service.caradium.zip).

Move the zip file to a location that can be accessed from Kodi, for example to the downloads [SMB share](https://wiki.libreelec.tv/accessing_libreelec#tab__sambasmb) LibreELEC.

Then, use Kodi to install the Add-ons repository from the downloaded zip file, as described [here](https://kodi.wiki/view/Add-on_manager#How_to_install_from_a_ZIP_file).

The Caradium Add-ons repository will reconfigure itself based on the device's architecture.

Finally, restart Kodi for the reconfiguration to take effect.

You can now manage (install, update, uninstall, etc.) all the add-ons of the Caradium Add-ons repository with the Kodi Add-on manager, as described [here](https://kodi.wiki/view/Add-on_manager).


## Add-on Summary

| Port                                | Add-on                                            | Function                 | Status                   |
| ----------------------------------- | ------------------------------------------------- | ------------------------ | ------------------------ |
| [6767](http://libreelec.local:6767) | [Bazarr](https://github.com/morpheus65535/bazarr) | subtitle manager         | Maybe                    |
| [8686](http://libreelec.local:8686) | [Lidarr](https://lidarr.audio/)                   | music manager            | Maybe                    |
| [8081](http://libreelec.local:8081) | [Medusa](https://github.com/pymedusa/Medusa)      | series manager           | Will do                  |
| [7878](http://libreelec.local:7878) | [Radarr](https://radarr.video/)                   | movie manager            | Maybe                    |
| [8989](http://libreelec.local:8989) | [Sonarr](https://sonarr.tv/)                      | series manager           | Will do                  |
| [9091](http://libreelec.local:9091) | [Transmission](https://transmissionbt.com/)       | bittorrent manager       | Will do                  |
|                                     | [ZeroTier One](https://www.zerotier.com/)         | virtual private network  | Probably                 |

## Feedback

The preferred way to submit bugs, comments and feature requests are GitHub issues.

Pull requests are welcome too.
