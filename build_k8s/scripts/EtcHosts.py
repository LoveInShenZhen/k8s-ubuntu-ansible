#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import Enum
from typing import List
from typing import Callable
import argparse


class EntryType(Enum):
    EmptyLine = 1
    Comments = 2
    HostEntry = 3


def entry_type_of(line: str) -> EntryType:
    if line.strip() == '':
        return EntryType.EmptyLine
    elif line.strip().startswith('#'):
        return EntryType.Comments
    else:
        return EntryType.HostEntry


class EntryItem(object):
    def __init__(self):
        self.entry_type = EntryType.EmptyLine

    def contain_ip(self, ip: str) -> bool:
        return False

    def contain_host(self, host: str) -> bool:
        return False

    def match(self, ip: str, host: str) -> bool:
        return False

    def remove(self, ip: str, host: str) -> bool:
        return False

    def remove_host(self, host: str) -> bool:
        return False

    def valid(self) -> bool:
        """
        判断该条目是否合法
        @return:
        """
        return True


class EmptyLine(EntryItem):
    def __init__(self):
        super().__init__()
        self.entry_type = EntryType.EmptyLine

    def __str__(self) -> str:
        return ''


class Comments(EntryItem):
    def __init__(self, line: str):
        super().__init__()
        self.content = line
        self.entry_type = EntryType.Comments

    def __str__(self) -> str:
        return self.content


class HostEntry(EntryItem):
    def __init__(self, ip: str = '', host_names: List[str] = []):
        super().__init__()
        self.entry_type = EntryType.HostEntry
        self.ip: str = ip
        self.names: List[str] = host_names

    def parse(self, line: str):
        parts = line.split()
        self.ip: str = parts[0]
        self.names: List[str] = parts[1:]

    def __str__(self) -> str:
        return f'{self.ip}    {"  ".join(self.names)}'

    def contain_ip(self, ip: str) -> bool:
        return self.ip == ip

    def contain_host(self, host: str) -> bool:
        return host in self.names

    def match(self, ip: str, host: str) -> bool:
        return self.contain_ip(ip) and self.contain_host(host)

    def remove(self, ip: str, host: str) -> bool:
        if self.match(ip, host):
            self.names.remove(host)
            return True
        else:
            return False

    def remove_host(self, host: str) -> bool:
        if self.contain_host(host):
            self.names.remove(host)
            return True
        else:
            return False

    def valid(self) -> bool:
        return len(self.names) > 0


class EtcHostsFile(object):
    def __init__(self, path: str = '/etc/hosts'):
        self.path = path
        self.entries: List[EntryItem] = self.__loadEtcHosts__()
        self.changed = False

    def __loadEtcHosts__(self) -> List[EntryItem]:
        with open(self.path) as f:
            return [self.__parseLine__(line.strip()) for line in f.readlines()]

    def __parseLine__(self, line: str) -> EntryItem:
        entry_type = entry_type_of(line)
        if entry_type == EntryType.EmptyLine:
            return EmptyLine()
        elif entry_type == EntryType.Comments:
            return Comments(line)
        else:
            entry = HostEntry()
            entry.parse(line)
            return entry

    def save(self, fpath: str = '') -> bool:
        """
        文件更新了, 则返回 True, 没有更新则返回 False
        @param fpath: 文件路径
        @return:
        """
        if not self.changed:
            return self.changed

        if fpath == '':
            fpath = self.path
        lines = [str(item) for item in self.entries]
        with open(fpath, 'w') as f:
            f.write('\n'.join(lines))
        return self.changed

    def clean_invalid_entries(self):
        filter_func: Callable[[EntryItem],
                              bool] = lambda item: item.valid()
        # 保留有效的
        new_entries = list(filter(filter_func, self.entries))
        if len(new_entries) != len(self.entries):
            self.changed = True
            self.entries = new_entries

    def remove(self, ip: str, host: str):
        if ip == '' and host == '':
            return
        elif ip != '' and host == '':
            # just remove by ip
            self.remove_ip(ip)
        elif ip == '' and host != '':
            # just remove by host
            self.remove_host(host)
        else:
            # remove by ip and host (match both)
            for entry in self.entries:
                if entry.remove(ip, host):
                    self.changed = True

        self.clean_invalid_entries()

    def remove_ip(self, ip: str):
        filter_func: Callable[[EntryItem],
                              bool] = lambda item: not item.contain_ip(ip)
        # 过滤掉包含该 ip 的(保留不包含该 ip 的)
        new_entries = list(filter(filter_func, self.entries))
        if len(new_entries) != len(self.entries):
            self.changed = True
            self.entries = new_entries

    def remove_host(self, host: str):
        for entry in self.entries:
            if entry.remove_host(host):
                self.changed = True

        self.clean_invalid_entries()

    def exists(self, ip: str, host: str) -> bool:
        for entry in self.entries:
            if entry.match(ip, host):
                return True
        # 没有匹配的
        return False

    def append(self, ip: str, host: str):
        if self.exists(ip, host):
            return
        else:
            self.entries.append(HostEntry(ip, [host]))
            self.changed = True


def main():
    parser = argparse.ArgumentParser(description = '/etc/hosts maintenance script')
    parser.add_argument('--ip',
                        help = 'ip address.',
                        default = '')
    parser.add_argument('--host',
                        help = 'host/domain name',
                        default = '')
    parser.add_argument('--state',
                        help = 'desired state.',
                        required = True,
                        choices = ['present', 'absent'])

    args = parser.parse_args()

    etc_host = EtcHostsFile()
    if args.state == 'present':
        etc_host.append(args.ip, args.host)
    else:
        etc_host.remove(args.ip, args.host)
    etc_host.save()


if __name__ == "__main__":
    main()
