# a class that has a lot of methods for getting relevant data from the api client
# uses the client to pass a api_client object, object is used for running calls for getting the data
from .get_loop_protect import LoopProtect
from .get_snmpv3_info import Snmpv3Info
from .get_sntp import SntpInfo
from .get_stp_info import StpInfo
from .interface_info import InterfaceInfo
from .lldp_neighbours import LLdpInfo
from .mac_table import MacAddressTable
from .port_info import PortInfo
from .pyaos_switch_client import PyAosSwitch
from .system_status import SystemStatus
from .telnet_info import TelnetInfo


#### TODO: OLD class to be deprecated !! replaced with class methods and pyaos_switch_client
class ArubaSwitchClient(object):
    def __init__(
        self,
        switch_ip,
        username,
        password,
        SSL=False,
        verbose=False,
        timeout=15,
        validate_ssl=False,
        rest_version=7,
    ):
        self.switch_ip = switch_ip
        self.username = username
        self.password = password
        self.SSL = SSL
        self.timeout = timeout
        self.verbose = verbose
        self.validate_ssl = validate_ssl
        self.rest_version = rest_version
        self.api_client = PyAosSwitch(
            switch_ip,
            self.username,
            self.password,
            SSL=self.SSL,
            verbose=self.verbose,
            timeout=self.timeout,
            validate_ssl=self.validate_ssl,
            rest_version=self.rest_version,
        )

    def get_telnet_server_status(self):
        """Returns true / false status of telnet server"""
        telnet_status = TelnetInfo(api_client=self.api_client)
        return telnet_status.get_telnet_status()

    def get_stp_info(self):
        """Returns stp-object containing stp-info."""
        stp = StpInfo(api_client=self.api_client)
        return stp.get_stp_info()

    def get_lldp_info_sorted(self):
        """Returns all switch/ap neighbour info as objects.
        requires rest-api v4"""
        lldp = LLdpInfo(api_client=self.api_client)
        return lldp.get_neighbours_sorted()

    def get_lldp_info(self):
        lldp = LLdpInfo(api_client=self.api_client)
        return lldp.get_neighbors()

    def get_snmpv3(self):
        """Returns snmpv3 info object"""
        snmpv3_info = Snmpv3Info(api_client=self.api_client)
        return snmpv3_info.get_snmpv3_info()

    def get_sntp(self):
        """Returns sntp server, list of objects with sntp-server info."""
        sntp_servers = SntpInfo(api_client=self.api_client)
        return sntp_servers.get_sntp_info()

    def get_loop_protected_ports(self):
        """Returns list of loop-protected ports"""
        loop_protect = LoopProtect(api_client=self.api_client).get_protected_ports()
        return loop_protect

    def get_non_loop_protected_ports(self):
        """Rerturns list of unprotected ports"""
        un_loop_protected = LoopProtect(api_client=self.api_client)
        return un_loop_protected.get_unprotected_ports()

    def get_transceivers(self):
        transceivers_data = InterfaceInfo(api_client=self.api_client).get_transceivers()
        return transceivers_data
