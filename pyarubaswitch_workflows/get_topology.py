from pyarubaswitch_workflows.runner import Runner
from pyarubaswitch.aruba_switch_client import ArubaSwitchClient
import csv

from pprint import pprint



class SwitchInfo(object):


    def __repr__(self):
        return f"switch_ip: {self.switch_ip}\nclients: {self.clients}\nwireless_clients: {self.wireless_clients}\n lldp_devices: {self.lldp_devices}"

    def __init__(self, switch_ip, clients, wireless_clients, lldp_devices):
        self.switch_ip = switch_ip # switch ip address
        self.clients = clients # list of clients
        self.wireless_clients = wireless_clients # list of WLANclients
        self.lldp_devices = lldp_devices # list OR dict of lldp_devices. if dict = ap_list , switch_list LISTS




class TopologyMapper(Runner):



    def export_topology_csv(self, csv_filename, topology_list):
        '''
        Exports topology data to csv-files
        '''
        # client file data export
        # mac-adress, port, wireless(YES/NO)
        client_header = ["switchip", "mac_address", "port","vlan_id", "Wireless"]
        client_file = f"{csv_filename}_clients.csv"

        with open(client_file, "w", encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(client_header)

            for switch_obj in topology_list:
                for client in switch_obj.clients:
                    row = [switch_obj.switch_ip, client.mac_address, client.port_id, client.vlan_id, ""]
                    writer.writerow(row)

                for client in switch_obj.wireless_clients:
                    row = [switch_obj.switch_ip, client.mac_address, client.port_id, client.vlan_id, "YES"]
                    writer.writerow(row)
            

        # uplink file data export
        uplink_header = ["switchip", "name", "port", "remote_port", "ip_address", "Type"]
        # append uplink_ports
        uplink_file = f"{csv_filename}_netdevices.csv"
        # append ap_ports
        with open(uplink_file, "w", encoding="UTF8") as f:
            writer = csv.writer(f)
            writer.writerow(uplink_header)

            
            for switch_obj in topology_list:
                if "ap_list" in switch_obj.lldp_devices:
                    for ap in switch_obj.lldp_devices["ap_list"]:
                        row = [switch_obj.switch_ip, ap.name, ap.local_port, ap.remote_port, ap.ip_address, "AP"]
                        writer.writerow(row)
                if "switch_list" in switch_obj.lldp_devices:
                    for switch in switch_obj.lldp_devices["switch_list"]:
                        row = [switch_obj.switch_ip, switch.name, switch.local_port, switch.remote_port, switch.ip_address, "Switch"]
                        writer.writerow(row)
                
                if type(switch_obj.lldp_devices) == list:
                    for device in switch_obj.lldp_devices:
                        row = [switch_obj.switch_ip, device.name, device.local_port, device.remote_port, device.ip_address, ""]
                        writer.writerow(row)
    




    def get_topology(self):
        '''
        Maps network toplogy
        '''
        # create topology list to return
        topology = []
        # create apiclient objects
        for switch in self.switches:
            switch_client = ArubaSwitchClient(
                    switch, self.username, self.password, self.SSL, self.verbose, self.timeout, self.validate_ssl, self.rest_version)
            
            if self.verbose:
                print("Logging in...")
            switch_client.login()
            if switch_client.api_client.error:
                print("ERROR LOGIN:")
                print(switch_client.api_client.error)

            switch_client.set_rest_version()
            if switch_client.api_client.error:
                print("ERROR getting rest version:")
                print(switch_client.api_client.error)
            if self.verbose:
                print(f"Using rest-version: {switch_client.rest_version}")

            mac_table = self.get_mac_table(switch_client)

            print("Getting lldp data")
            if switch_client.api_client.legacy_api:
                lldp_data = self.get_lldp_info(switch_client)
            else:
                lldp_data = self.get_lldp_info_sorted(switch_client)

            
            uplink_ports = []
            wireless_ports = []

            # lldp-data can be a dict of: 
            # ap_list: [list-of,aps]
            # switch_list: [list-of,switches]
            # or if using legacy api, one big list of devices
            if switch_client.api_client.legacy_api:
                for entry in lldp_data:
                    uplink_ports.append(entry.local_port)
            else:
                for entry in lldp_data["ap_list"]:
                    wireless_ports.append(entry.local_port)
                for entry in lldp_data["switch_list"]:
                    uplink_ports.append(entry.local_port)
           
            
            clients = []
            for entry in mac_table:
                if entry.port_id not in uplink_ports and entry.port_id not in wireless_ports:
                    clients.append(entry)
            wireless_clients = []
            for entry in mac_table:
                if entry.port_id in wireless_ports:
                    wireless_clients.append(entry)
            
            # sorting wireless and wired clients only works if api has version4 or greater
            print("Wired clients")
            pprint(clients)
            print("WLAN clients")
            pprint(wireless_clients)

            # create switchobject
            sw_obj = SwitchInfo(switch_ip=switch, clients=clients, wireless_clients=wireless_clients, lldp_devices=lldp_data)
            topology.append(sw_obj)

            #self.export_topology_csv(switchip=switch, clients=clients, wireless_clients=wireless_clients, lldp_devices=lldp_data)

            switch_client.logout()

        return topology





    def get_mac_table(self, api_runner):
        '''
        :params api_runner   ArubaSwitchClient object
        Get mac-address table from switch
        '''
        switch_client = api_runner
               
        if switch_client.api_client.error:
            print(switch_client.api_client.error)
            exit(0)

        if self.verbose:
            print("Getting mac-address table")
        mac_table = switch_client.get_mac_address_table()

        return mac_table

    


