from pathlib import Path

import yaml

from .pyaos_switch_client import PyAosSwitchClient


class ConfigParseError(Exception):
    """
    Error parsing config
    """

    pass


class ConfigReader(object):
    def __init__(self, filepath):
        self.filepath = filepath

        # try to read file, if doesnt exist. exit app
        if Path(self.filepath).is_file():
            self.vars = self.read_yaml(self.filepath)

            self.username = self.vars['username']
            self.password = self.vars['password']
            self.switches = self.vars['switches']
            if 'use_ssl' in self.vars:
                self.use_ssl = self.vars['use_ssl']
            else:
                self.use_ssl = False
            if 'log_level' in self.vars:
                self.log_level = self.vars['log_level']
            else:
                self.log_level = None
            if 'site_name' in self.vars:
                self.site_name = self.vars['site_name']
        else:
            raise ConfigParseError(f'Error! No configfile was found:\n{self.filepath}')

    def read_yaml(self, filename):
        """Get username password and IP of switches from file"""
        with open(filename, 'r') as input_file:
            data = yaml.load(input_file, Loader=yaml.FullLoader)
        return data

    def get_apiclient_from_file(self, ip_addr: str) -> PyAosSwitchClient:
        """
        Takes yaml file, returns ArubaSwitchClient object

        args:
        ip_addr(str)Optional: str format ip-adress of switch to return a client.

        Returns:
            PyAosSwitchClient: API-Client object.
        """
        if self.log_level is not None:
            return PyAosSwitchClient(
                ip_addr=ip_addr,
                username=self.username,
                password=self.password,
                SSL=self.use_ssl,
                log_level=self.log_level,
            )
        else:
            return PyAosSwitchClient(
                ip_addr=ip_addr,
                username=self.username,
                password=self.password,
                SSL=self.use_ssl,
            )
