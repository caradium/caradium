""" default.py

This is the entrypoint for the add-on.

The script determines the version, project and architecture that the
system is currently running.

More information can be found at https://kodi.wiki/view/Add-on_development.

If the Kodi version, project or architecture is not supported, then
an issue will nned to be opened at https://github.com/caradium/caradium.

This script requires xbmc, xbmcaddon and xbmcgui as well some python
builtin libraries like xml and os.

This contains the following
functions:
    * log - write a message to the kodi logs
    * update - update the addon.xml
    * main - the main function of the script
"""
import os.path
import xbmc
import xbmcaddon
import xbmcgui
import xml.etree.ElementTree as etree


def log(message):
    xbmc.log(f"caradium: {message}", xbmc.LOGINFO)


def evaluate_system(repositories) -> (str, str, str):
    for repo in repositories:
        try:
            addon = xbmcaddon.Addon(repo)
            addon_path = addon.getAddonInfo('path')
            addon_xml_path =  os.path.join(addon_path, 'addon.xml')
            xml = etree.parse(addon_xml_path)
            datadir = next(xml.iter(tag='datadir'))
            vers, proj, arch = datadir.text.rstrip('/').split('/')[-3:]
            log('found {}/{}/{} in {}'.format(vers, proj, arch, repo))
            return vers, proj, arch
        except:
            log(f'unable to parse {repo}')
            continue
    return '', '', ''


def get_addon_xml(addon: xbmcaddon.Addon) -> etree.ElementTree:
    addon_path = addon.getAddonInfo('path')
    addon_xml_path = os.path.join(addon_path, 'addon.xml')
    xml = etree.parse(addon_xml_path)
    return xml


def update_addon_xml(addon: xbmcaddon.Addon, url: str) -> etree.ElementTree:
    addon_path = addon.getAddonInfo('path')
    addon_xml_path = os.path.join(addon_path, 'addon.xml')
    xml = etree.parse(addon_xml_path)
    datadir = next(xml.iter(tag='datadir'))
    datadir.text = url
    next(xml.iter(tag='info')).text = url + 'addons.xml'
    next(xml.iter(tag='checksum')).text = url + 'addons.xml.md5'
    xml.write(addon_xml_path)
    addon.setSetting('updated', 'true')
    return xml


def main():
    addon_base_url = 'https://raw.githubusercontent.com/caradium/caradium/main/addons/{}/{}/'
    official_repositories = ['repository.libreelec.tv', 'repository.coreelec']
    addon = xbmcaddon.Addon()
    addon_strings = addon.getLocalizedString

    version, project, architecture = evaluate_system(official_repositories)

    if not version or not project or not architecture:
        log('unable to find a known distribution')
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('Caradium', 'There was an error determining the project architecture.\nPlease open an issue at '
                                   'https://github.com/caradium/caradium with information about the Kodi version, '
                                   'the project and the architecture.')
        return ok

    addon.setSetting('distribution', addon_strings(33003).format(version, project, architecture))
    url = addon_base_url.format('armv8', architecture)  ## Only supporting armv8 for now.
    addon_was_updated = addon.getSetting('updated')

    if addon_was_updated == 'false':
        log('respository is already up to date. Exiting...')
        return None

    if addon_was_updated == 'true':
        log('respoitory addon.xml was updated. Calling kodi to update addon repos...')
        addon.setSetting('updated', 'false')
        xbmc.executebuiltin('UpdateAddonRepos')
        log('updated the addon repos')
        return None

    xml = get_addon_xml(addon)
    datadir = next(xml.iter(tag='datadir'))

    if datadir.text != url:
        update_addon_xml(addon, url)
        log('updated repository')
        dialog = xbmcgui.Dialog()
        if not dialog.yesno(
                addon.getAddonInfo('name'),
                addon_strings(33010).format(version, project, architecture),
                nolabel=addon_strings(33011),
                yeslabel=addon_strings(33012)
        ):
            xbmc.executebuiltin('RestartApp')


if __name__ == '__main__':
    main()
