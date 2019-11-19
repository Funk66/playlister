from yaml import load, dump
from logging import getLogger, basicConfig
from pathlib import Path
from typing import Any
from argparse import ArgumentParser, Namespace


class ConfigError(Exception):
    def __init__(self, param: str):
        self.param = param

    def __str__(self) -> str:
        return f"'{self.param}' is not a valid configuration parameter"


class MetaConfig(type):
    def __new__(mcs, name, bases, namespace):
        fields = namespace['__annotations__'].keys()
        meta = {
            'data': dict(zip(fields, [''] * len(fields))),
            'loaded': False,
            'path': Path.home() / '.config/playlister/config.yaml',
        }
        return super().__new__(mcs, name, bases, {
            **namespace, '__meta__': meta
        })

    def __getattr__(self, name: str) -> Any:
        if name not in self.__meta__['data']:
            raise ConfigError(name)
        if not self.__meta__['loaded']:
            self.load()
        return self.__meta__['data'][name]

    def __setattr__(self, name: str, value: Any) -> None:
        self.update(**{name: value})

    def load(self) -> None:
        if self.__meta__['path'].exists():
            with open(self.__meta__['path']) as data:
                log.info('Reading config file')
                self.__meta__['data'].update(load(data))
        self.__meta__['loaded'] = True

    def write(self) -> None:
        path = self.__meta__['path']
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        with open(path, 'w') as output:
            log.info('Writing config file')
            dump(self.__meta__['data'], output, default_flow_style=False)

    def update(self, **kwargs) -> None:
        for name, value in kwargs.items():
            if name not in self.__meta__['data']:
                raise ConfigError(name)
            if not self.__meta__['loaded']:
                self.load()
            self.__meta__['data'][name] = value
        self.write()


class Config(metaclass=MetaConfig):
    client: str
    secret: str
    token: str
    refresh: str
    validity: float


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


log = getLogger('playlister')
logging()
