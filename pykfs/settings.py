import os.path
import yaml


def get_default_settings_file_path():
    return os.path.expanduser("~/.pykfsrc")


def get_script_settings(script_name, settings_file=None):
    settings = {}
    if script_name:
        d = get_settings_dict(settings_file)
        settings = d and d["scripts"][script_name] or {}
    return settings


def get_settings_dict(settings_file=None):
    if not settings_file:
        settings_file = get_default_settings_file_path()
    if not os.path.isfile(settings_file):
        return None
    d = None
    with open(settings_file) as f:
        d = yaml.load(f)
    return d



