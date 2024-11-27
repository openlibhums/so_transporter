from utils import plugins

PLUGIN_NAME = 'Science Open Transporter Plugin'
DISPLAY_NAME = 'Science Open Transporter'
DESCRIPTION = 'FTP transporter for Science Open.'
AUTHOR = 'Andy Byers'
VERSION = '0.1'
SHORT_NAME = 'so_transporter'
MANAGER_URL = 'so_transporter_manager'
JANEWAY_VERSION = "1.7"


class So_transporterPlugin(plugins.Plugin):
    plugin_name = PLUGIN_NAME
    display_name = DISPLAY_NAME
    description = DESCRIPTION
    author = AUTHOR
    short_name = SHORT_NAME
    manager_url = MANAGER_URL

    version = VERSION
    janeway_version = JANEWAY_VERSION


def install():
    So_transporterPlugin.install()


def hook_registry():
    So_transporterPlugin.hook_registry()


def register_for_events():
    pass
