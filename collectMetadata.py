#!/usr/bin/env python
#
# Copyright 2016 HLRS, University of Stuttgart
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Package to hold classes for meta data collection of one host."""

# @Author: Uwe Schilling, schilling@hlrs.de
# @COMPANY: HLRS, University of Stuttgart
# @Date: 2016-11-22


import logging
from os import path, makedirs, environ
import datetime
import platform
import subprocess
import json
import click


class Collector(object):
    """collects metadata for one host."""

    def __init__(self):
        """Init of this class."""
        self.logger = self.get_logger()
        self.hostname = self.collect_hostname()

    def get_logger(self):
        """Setup the global logger."""
        # log setup
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        # create formatter and add it to the handlers
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        # add the handlers to the logger
        logger.addHandler(ch)
        logger.debug('Logger setup complete. Start Program ... ')
        return logger

    def collect_cpu_info(self):
        """Get cpu info."""
        self.logger.info('getting cpu info.')
        import cpuinfo
        return cpuinfo.get_cpu_info()

    def collect_packages(self):
        """Get packages installed."""
        self.logger.info('getting installed packages and there version.')
        import apt
        cache = apt.Cache()

        pkg_list = {}

        for pkg in cache.keys():
            if cache[pkg].is_installed:
                pkg_list[cache[pkg].name] = str(cache[pkg].versions)

        return pkg_list

    def collect_env(self):
        """Get environment variables."""
        self.logger.info('getting the environment.')
        return dict(environ)

    def collect_hostname(self):
        """Get host name."""
        self.logger.info('getting the host name.')
        return platform.node()

    def collect_processes(self):
        """Get running processes."""
        self.logger.info('getting running processes.')
        import psutil
        pl = []
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name'])
            except psutil.NoSuchProcess:
                pass
            else:
                pl.append(pinfo)
        return pl

    def get_date(self):
        """Get the current date time."""
        import time
        self.logger.info('getting the time.')
        result_dict = {}
        date_dict = {'date': str(datetime.datetime.now())}
        ts_dict = {'time_stamp': time.time()}

        result_dict.update(date_dict)
        result_dict.update(ts_dict)

        return result_dict

    def get_mpi_version(self):
        """Get the mpi version and path."""
        self.logger.info('getting mpi version.')
        out = {}
        out['path'] = subprocess.check_output(["which", "mpirun"])
        tmp = subprocess.check_output(
            ["mpirun", "--version"], stderr=subprocess.STDOUT)
        out['version'] = tmp.split('\n')[0]
        return out

    def get_gitpath_version(self, path):
        """Merge the meta data form multiple nodes into one document."""
        self.logger.info('getting last git commit id of %s.' % path)
        from sh import git
        git = git.bake("-C", path)
        git_out = git.describe('--always')
        return git_out.rstrip()

    def get_users(self):
        """Get all users and their groups."""
        self.logger.info('getting user info.')
        import pwd
        import grp
        return_dict = {}
        groups_list = grp.getgrall()

        for user in pwd.getpwall():
            user_group_list = []
            # skip all user accounts that are not allowed/capable to login
            if ('/bin/false' not in user[6] and
                    '/usr/sbin/nologin' not in user[6] and
                    '/home' in user[5]):
                user_group_list.append(grp.getgrgid(user[3])[0])
                for group in groups_list:
                    if user[0] in group[3]:
                        user_group_list.append(group[0])
                if len(user_group_list) > 0:
                    return_dict[user[0]] = user_group_list
        return return_dict

    def get_network(self):
        """Get all network interface informations."""
        self.logger.info('getting network info.')
        import netifaces
        return_dict = {}
        return_dict['ip_v4_gateways'] = netifaces.gateways()
        link_list = netifaces.interfaces()
        for link in link_list:
            return_dict[link] = netifaces.ifaddresses(link)

        return return_dict

    def get_vms(self):
        """Get VMs active / not active."""
        self.logger.info('getting vm(s) info.')
        import libvirt
        import sys

        conn = libvirt.open('qemu:///system')
        if conn is None:
            self.logger.warning(
                'Error in libvirt qemu connection:\n {}'.format(sys.stderr)
            )
            return

        domain_names = conn.listDefinedDomains()

        if len(domain_names) <= 0:
            return ['no_vms']
        domain_ids = conn.listDomainsID()
        if domain_ids is None:
            self.logger.warning(
                'Error in libvirt domain collection:\n {}'.format(sys.stderr)
            )
            return
        return_dict = {}
        return_dict['inactive_vms'] = domain_names
        return_dict['active_vms'] = {}
        if len(domain_ids) >= 0:
            for domainID in domain_ids:
                domain = conn.lookupByID(domainID)
                return_dict['active_vms'][domain.name()] = {
                    'os_type': domain.OSType(),
                    'id': domain.ID(),
                    'infos': {
                        'state': domain.info()[0],
                        'max_memory': domain.info()[1],
                        'memory': domain.info()[2],
                        'nb_virt_cpu': domain.info()[3],
                        'cpu_time': domain.info()[4]
                    }

                }

        conn.close()
        return return_dict

    def get_mounts(self):
        """Get Physical disc / nfs mounts."""
        self.logger.info('getting mounts.')
        import psutil
        partitions_disks = psutil.disk_partitions(all=False)
        partitions_all = psutil.disk_partitions(all=True)

        for disc in partitions_all:
            for fild in disc:
                if 'nfs' in fild:
                    partitions_disks.append(disc)
                    break
        return partitions_disks


def get_metatdata(coll):
    """Get all the data."""
    metadata = {}
    metadata['env'] = coll.collect_env()
    metadata['packages'] = coll.collect_packages()
    metadata['processes'] = coll.collect_processes()
    metadata['time'] = coll.get_date()
    metadata['cpu'] = coll.collect_cpu_info()
    metadata['mpi'] = coll.get_mpi_version()
    metadata['vTorque'] = coll.get_gitpath_version('...')
    return {coll.collect_hostname(): metadata}


@click.command()
@click.option(
    '--input_path',
    type=click.Path(),
    help='the path to the directory containing the json files',
    required=True)
def main(input_path):
    """
    Collect information of this node and saves it to a json file.

    Click is used to build help and pares input.
    --input_path    the path to the where the json file should be written.
    """
    metadata_path = input_path
    print 'write to %s' % metadata_path

    # see if path exist
    try:
        if not path.exists(metadata_path):
            print('path %s dose not exist, try to create it.' % metadata_path)
            makedirs(metadata_path)
    except Exception as e:
        raise e

    # collect data
    print('collecting data...')
    coll = Collector()
    out = get_metatdata(coll)

    nodename = str(out.keys()[0])

    # write file out
    json_path = str('%s/%s.json' % (metadata_path, nodename))

    if path.exists(json_path):
        print(
            '%s already exists. please check if it is created by someone else'
            % json_path)
        exit()

    with open(json_path, 'w') as fp:
        json.dump(out, fp)

if __name__ == '__main__':
    # Start now!
    main()
