import pytest
import shutil
import pathlib
import importlib.util
from xbmcgui import Dialog
from xbmcaddon import Addon
import xml.etree.ElementTree as etree

PROJECT_DIR = pathlib.Path(__file__).parent.parent

@pytest.fixture
def setup(tmp_path):
    d = tmp_path / "service.caradium"
    d.mkdir()
    shutil.copytree(PROJECT_DIR / "service.caradium", d, dirs_exist_ok=True)
    yield tmp_path

class TestAddon(Addon):
    def __init__(self, addon_id: str = "service.caradium", addon_directory: pathlib.Path = PROJECT_DIR):
        self.addon_id = addon_id
        self.addon_directory = addon_directory

    def getLocalizedString(self, number: int) -> str:
        with open(pathlib.Path(self.addon_directory / "service.caradium/resources/language/English/strings.po")) as language_file:
            strings = language_file.readlines()
        strings_dict, last_id = {}, None
        for i in strings:
            if i.startswith('msgctxt') and not i.strip().endswith('""'):
                id = i.split()[1].replace('"', '').replace('#', '')
                strings_dict.update({int(id): None})
                last_id = int(id)
            elif i.startswith("msgid") and not i.strip().endswith('""'):
                text = i.split()[1].replace('"', '')
                strings_dict.update({last_id: text})
                last_id = None
            else:
                last_id = None
        return strings_dict[number]

    def getAddonInfo(self, attribute: str) -> str:
        if attribute == 'path':
            if self.addon_id == "repository.coreelec":
                return f"{PROJECT_DIR}/tests/resources/repository.coreelec"
            return f"{self.addon_directory}/service.caradium"
        addon_xml = etree.parse(f"{self.addon_directory}/service.caradium/addon.xml")
        if attribute == 'name':
            root = addon_xml.getroot()
            return root.attrib['name']
        return attribute

    def setSetting(self, id: str, value: str) -> None:
        settings_xml = etree.parse(f"{self.addon_directory}/service.caradium/resources/settings.xml")
        root = settings_xml.getroot()
        for e in root.iter():
            if 'id' in e.attrib:
                if e.attrib['id'] == id:
                    e.text = value
                    settings_xml.write(f"{self.addon_directory}/service.caradium/resources/settings.xml")
                    return None
            last_element = e
        new_setting = etree.Element('setting')
        new_setting.attrib['label'] = str( int(last_element.attrib['label']) + 1 )
        new_setting.attrib['type'] = 'text'
        new_setting.attrib['enable'] = 'false'
        new_setting.attrib['id'] = id
        new_setting.text = value
        root.find('category').append(new_setting)
        settings_xml.write(f"{self.addon_directory}/service.caradium/resources/settings.xml")
        return None

    def getSetting(self, id: str) -> str:
        settings_xml = etree.parse(f"{self.addon_directory}/service.caradium/resources/settings.xml")
        root = settings_xml.getroot()
        for e in root.iter():
            if 'id' in e.attrib:
                if e.attrib['id'] == id:
                    element = e
                    return element.text
        return ''

class TestDialog(Dialog):
    DLG_YESNO_NO_BTN = 10

    def yesno(self, heading: str,
              message: str,
              nolabel: str = "",
              yeslabel: str = "",
              autoclose: int = 0,
              defaultbutton: int = DLG_YESNO_NO_BTN) -> bool:
        print(
            f"""
            ###############################################################
            #                        {heading}
            ###############################################################
            #                        {message}
            #                                                             #
            #             {yeslabel}               {nolabel}
            ###############################################################
            """
        )
        return True

    def ok(self, heading: str, message: str) -> bool:
        print(
            f"""
            ###############################################################
            #                        {heading}
            ###############################################################
            #{message}
            ###############################################################
            """
        )
        return True

def test_log(mocker, capsys):
    class PropertyMock(mocker.PropertyMock):
        def __repr__(self):
            return f"{self.return_value}"

    mocker.patch('xbmc.log', wraps=print)
    mocker.patch('xbmc.LOGINFO', new_callable=PropertyMock, return_value='INFO')

    spec = importlib.util.spec_from_file_location(
        name="default",
        location=f"{PROJECT_DIR}/service.caradium/default.py",
    )
    default = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(default)

    default.log('This is a test')
    out, err = capsys.readouterr()
    assert "caradium: This is a test INFO\n" in out


def test_evaluate_system_returns_nothing():

    spec = importlib.util.spec_from_file_location(
        name="default",
        location=f"{PROJECT_DIR}/service.caradium/default.py",
    )
    default = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(default)

    assert default.evaluate_system([]) == ('', '', '')

def test_evaluate_system_returns_correct_project_version_and_architecture(mocker):
    def addon_factory():
        for id in ['', 'repository.coreelec']:
            if id:
                yield TestAddon(id)
            else:
                yield TestAddon()
    mocker.patch('xbmcaddon.Addon', side_effect=addon_factory(), create=True, return_value=TestAddon)

    spec = importlib.util.spec_from_file_location(
        name="default",
        location=f"{PROJECT_DIR}/service.caradium/default.py",
    )
    default = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(default)

    assert default.evaluate_system(['repository.fake', 'repository.coreelec']) == ('9.2', 'Amlogic', 'arm')

def test_get_addon_xml(mocker):
    addon = TestAddon()
    mocker.patch('xbmcaddon.Addon', return_value=TestAddon)

    spec = importlib.util.spec_from_file_location(
        name="default",
        location=f"{PROJECT_DIR}/service.caradium/default.py",
    )
    default = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(default)

    xml = default.get_addon_xml(addon)

    root = xml.getroot()
    assert root.text.strip() == ''
    assert root.attrib['id'] == "service.caradium"
    assert root.attrib['name'] == "Caradium Add-ons"
    assert 'version' in root.attrib
    assert root.attrib['provider-name'] == "caradium"

    for e in root.iter('requires/import'):
        assert e.attrib['addon'] == "xbmc.python"
        assert e.attrib['python'] == "3.0.0"

    assert next(e for e in root.iter('extension') if e.attrib['point'] == 'xbmc.service').attrib['library'] == 'default.py'

    for e in next(e for e in root.iter('extension') if e.attrib['point'] == 'xbmc.addon.repository'):
        assert e.text == 'TBD'
        assert e.tag in ['datadir', 'info', 'checksum']
        if e.tag == 'datadir':
            assert e.attrib['zip'] == 'true'

def test_update_addon_xml(setup):
    addon = TestAddon(addon_directory=setup)

    spec = importlib.util.spec_from_file_location(
        name="default",
        location=f"{PROJECT_DIR}/service.caradium/default.py",
    )
    default = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(default)

    xml = default.update_addon_xml(addon, 'http://github/url/')

    root =  xml.getroot()
    for e in next(e for e in root.iter('extension') if e.attrib['point'] == 'xbmc.addon.repository'):
        assert e.text != 'TBD'
        assert e.tag in ['datadir', 'info', 'checksum']
        if e.tag == 'datadir':
            assert e.text == 'http://github/url/'
        if e.tag == 'info':
            assert e.text == 'http://github/url/addons.xml'
        if e.tag == 'checksum':
            assert e.text == 'http://github/url/addons.xml.md5'

def test_main_fails_with_a_dialog_notification(mocker, setup, capsys):
    addon = TestAddon(addon_directory=setup)
    mocker.patch('xbmcaddon.Addon', return_value=addon)
    dialog = TestDialog()
    mocker.patch('xbmcgui.Dialog', return_value=dialog)
    mocker.patch('xbmc.log', wraps=print)
    mocker.patch('xbmc.LOGINFO', new_callable=mocker.PropertyMock, return_value='INFO')
    mocker.patch('xbmc.executebuiltin', wraps=print)

    spec = importlib.util.spec_from_file_location(
        name="default",
        location=f"{PROJECT_DIR}/service.caradium/default.py",
    )
    default = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(default)

    default.main()

    out, err = capsys.readouterr()
    assert 'There was an error determining the project architecture' in out

def test_main_does_not_update_each_time(mocker, setup, capsys):
    def addon_factory():
        for id in ['', '', 'repository.coreelec', '', '', 'repository.coreelec', '', '', 'repository.coreelec']:
            if id:
                yield TestAddon(addon_id=id, addon_directory=setup)
            else:
                yield TestAddon(addon_directory=setup)
    mocker.patch('xbmcaddon.Addon', side_effect=addon_factory(), create=True)
    dialog = TestDialog()
    mocker.patch('xbmcgui.Dialog', return_value=dialog)
    mocker.patch('xbmc.log', wraps=print)
    mocker.patch('xbmc.LOGINFO', new_callable=mocker.PropertyMock, return_value='INFO')
    mocker.patch('xbmc.executebuiltin', wraps=print)

    spec = importlib.util.spec_from_file_location(
        name="default",
        location=f"{PROJECT_DIR}/service.caradium/default.py",
    )
    default = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(default)

    default.main()
    default.main()
    default.main()

    out, err = capsys.readouterr()
    assert 'respository is already up to date. Exiting...' in out
