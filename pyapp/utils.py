import os

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data(path):
    return os.path.join(_ROOT, 'map', 'data', path)


def get_figures(path):
    return os.path.join(_ROOT, 'map', 'figures', path)


def get_log_file():
    return os.path.join(_ROOT, "logs", "model_viewer.log")


def get_data_vc(path):
    return os.path.join(_ROOT, 'vc', 'data', path)


def get_figures_vc(path):
    return os.path.join(_ROOT, 'vc', 'figures', path)
