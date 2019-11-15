from yaml import load, dump
from logging import getLogger, basicConfig
from pathlib import Path
from typing import Union, Dict
from argparse import ArgumentParser, Namespace


class MetaConfig(type):
    def __new__(mcs, name, bases, namespace):
        namespace['data']: Dict[str, Union[str, int]] = {}
        for key, value in namespace['__annotations__'].items():
            namespace['data'][key] = namespace.get(key)
        return super().__new__(mcs, name, bases, namespace)


class Config(metaclass=MetaConfig):
    client: str
    secret: str
    token: str
    refresh: str
    validity: str
    path = Path.home() / '.config/playlister/config.yaml'

    def __init__(self, path: Path = None):
        if path:
            self.path = path
        if not self.path.exists():
            log.warning('No configuration available')
            self.path.parent.mkdir(parents=True, exist_ok=True)
        else:
            with open(self.path) as data:
                self.data.update(load(data))

    def __getattr__(self, attr):
        try:
            return self.data[attr]
        except KeyError:
            raise AttributeError(
                f"'{attr}' is not a valid configuration parameter")

    def __setattr__(self, attr, value) -> None:
        if attr not in self.data:
            raise AttributeError(
                f"'{attr}' is not a valid configuration parameter")
        self.data[attr] = value
        with open(self.path, 'w') as output:
            log.info('Updating config')
            dump(self.data, output, default_flow_style=False)


def arguments() -> Namespace:
    parser = ArgumentParser(description='')
    parser.add_argument('-t', '--token', help='Token')
    parser.add_argument('-c', '--client', help='Client id')
    parser.add_argument('-s', '--secret', help='Client secret')
    parser.add_argument('-r', '--redirect', help='Redirect URL')
    parser.add_argument('-p', '--path', help='Path to the config file')
    return parser.parse_args()


def logging():
    basicConfig(level=10, format='%(message)s')


def init():
    pass


config = None
log = getLogger('playlister')
logging()
