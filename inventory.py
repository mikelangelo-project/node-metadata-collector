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

"""get host informations."""

# @Author: Uwe Schilling, schilling@hlrs.de
# @COMPANY: HLRS, University of Stuttgart
# @Date: 2016-02-23

import click
from collectMetadata import Collector
from mergeMetadata import MergeMetadata
from database import JsonConnector


def _inventory_show(je, show, list_keys, host):

    if host and list_keys:
        print('Available keys:')
        je.get_host_keys(host)
        exit()
    elif host and show:
        print('Data for {} {}:'.format(host, show))
        je.get_host_value_to_key(host, show)
    elif list_keys and show:
        je.get_all_host_keys(show)
    elif show:
        print('Data for {}:'.format(show))
        je.get_host_infos(show)
        exit()
    elif host:
        print('Data for {}:'.format(host))
        je.get_host_infos(host)
        exit()
    elif list_keys:
        print('Host list:')
        je.list_hosts()
        exit()
    else:
        print('Try --help to see help')


def _inventory_collect(je, collect, out_path):

    host_informations = Collector()
    host = host_informations.hostname
    update_dict = {host: {}}
    update_dict[host]['network'] = host_informations.get_network()
    update_dict[host]['vms'] = host_informations.get_vms()
    update_dict[host]['users'] = host_informations.get_users()
    update_dict[host]['mounts'] = host_informations.get_mounts()
    update_dict[host]['storage'] = {"get_info": []}
    update_dict[host]['comment'] = ""
    update_dict[host]['collection_time'] = host_informations.get_date()

    if out_path:
        je.dump_dict(update_dict, out_path)
    else:
        je.add_host(update_dict)
        je.save_dict()


def _inventory_mege(je, merge, out_path):

    if not merge:
        print('please provide input path -m [path]')
        exit(1)

    mm = MergeMetadata()
    mm.read_files(merge)
    mm.merge_files()
    if out_path:
        mm.save_new_json(out_path)
    else:
        mm.save_new_json('data/merge.json')


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    '-H',
    '--host',
    type=click.STRING,
    help='Name of the host that should be printed')
@click.option(
    '-d',
    '--dbfile',
    default='data/servers.json',
    type=click.Path(),
    help='Use non default db file')
@click.option(
    '-l',
    '--list_keys',
    default=False,
    is_flag=True,
    help='List all stored keys')
@click.option(
    '-s',
    '--show',
    type=click.STRING,
    help='Show content of key')
@click.option(
    '-c',
    '--collect',
    default=False,
    is_flag=True,
    help='Collect Information about this host')
@click.option(
    '-m',
    '--merge',
    type=click.Path(),
    help='Merge multiple JSON files in PATH into one inventory')
@click.option(
    '-o',
    '--out_path',
    type=click.STRING,
    help='Path to output file.')
def main(host, dbfile, list_keys, show, collect, merge, out_path):
    """Tool to explore meta data files."""
    je = JsonConnector(dbfile)

    if show or list_keys or host:
        # call show stuff
        _inventory_show(je, show, list_keys, host)
    elif collect:
        # collect
        _inventory_collect(je, collect, out_path)
    elif merge:
        # merge stuff
        _inventory_mege(je, merge, out_path)
    else:
        # assume miss use of the tool
        print('Try --help to see help')


if __name__ == '__main__':
    main()
