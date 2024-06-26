from typing import List, Optional  # List is required before python3.10

from pydantic import BaseModel


class STP(BaseModel):
    enabled: bool
    prio: int
    mode: str


class LldpNeighbour(BaseModel):
    local_port: str
    name: str
    ip_address: str
    remote_port: Optional[str] = None


class LLDPTable(BaseModel):
    switches: List[LldpNeighbour] = []
    access_points: List[LldpNeighbour] = []


class SntpServer(BaseModel):
    address: Optional[str] = None
    prio: Optional[int] = None


class Snmpv3(BaseModel):
    enabled: bool
    readonly: bool
    only_v3: bool


class Port(BaseModel):
    """
    Port info model.
    vlan tagged or untagged
    auth.mode
    """

    port_id: str  # str becase can be: 1 or 1/1/1 or a16
    untagged: Optional[int] = None
    tagged: Optional[List[int]] = None
    dot1x_enabled: Optional[bool] = None
    macauth_enabled: Optional[bool] = None
    lacp_status: Optional[str] = None
    trunk_group: Optional[str] = None


class VlanPort(Port):
    missing_untagged: Optional[List[int]] = []
    missing_tagged: Optional[List[int]] = []

    def check_desired_vlans(self, desired_untag, desired_tag):
        """Returns missing vlans that are defined as desired untag/tag"""
        for vlan in desired_untag:
            if vlan not in self.untagged:
                self.missing_untagged.append(vlan)
        for vlan in desired_tag:
            if vlan not in self.tagged:
                self.missing_tagged.append(vlan)

        return self.missing_untagged, self.missing_tagged
