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

"""Package to hold classes for data connectors."""

# @Author: Uwe Schilling, schilling@hlrs.de
# @COMPANY: HLRS, University of Stuttgart
# @Date: 2016-02-03

import logging
import json
import os


class JsonConnector(object):
    """Class to interact with the json file."""

    def __init__(self, path):
        """Class init."""
        self.json_file = path
        self.logger = self._get_logger()
        self.dict_server = self._get_dict_from_file()

    def _get_logger(self):
        """Setup the global logger."""
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

    def _get_dict_from_file(self):
        try:
            file = open(self.json_file)
            return_dict = json.load(file)
            file.close()
        except (IOError):
            self.logger.warning(
                'No database file found please check path: {}'.format(
                    self.json_file))
            db_pardir = os.path.abspath(os.path.join(
                self.json_file,
                os.pardir)
            )
            # create parent directory if not exist
            if not os.path.exists(db_pardir):
                self.logger.warning(
                    'Parent directory {} dose not exist.'.format(db_pardir)
                )
                self.logger.info('creating {}'.format(db_pardir))
                os.makedirs(db_pardir)
            # create new db
            self.logger.info('creating new db file: {}'.format(self.json_file))
            with open(self.json_file, 'wr') as file:
                self.logger.debug(self._get_default_dict())
                file.write(json.dumps(
                    self._get_default_dict(),
                    sort_keys=True,
                    indent=4)
                )
                file.close()
                return self._get_dict_from_file()
        except (ValueError) as e:
            self.logger.error(
                'something is wrong with the json file.\n{}'.format(e))
            exit(1)
        self.logger.debug(
            json.dumps(return_dict, sort_keys=True, indent=4)
        )
        return return_dict

    def get_host_infos(self, hostname):
        """Return informations to a host."""
        try:
            print_string = json.dumps(
                self.dict_server[hostname],
                sort_keys=True,
                indent=4
            )
            print(print_string)
        except (KeyError):
            self.logger.error(
                "Server informations not found for: {}".format(hostname)
            )

    def get_host_keys(self, hostname):
        """Get all keys stored for a host."""
        try:
            key_list = self.dict_server[hostname].keys()
        except (KeyError):
            self.logger.error(
                "Server informations not found for: {}".format(hostname)
            )
            exit(1)
        for key in sorted(key_list):
            print(key)

    def list_hosts(self):
        """List all stored hosts."""
        host_list = self.dict_server.keys()
        for host in sorted(host_list):
            print(host)

    def get_host_value_to_key(self, host, key):
        """Get a value to a key of a host."""
        try:
            print_string = json.dumps(
                self.dict_server[host][key],
                sort_keys=True,
                indent=4
            )
        except (KeyError):
            self.logger.error(
                "Server informations not found for: host:"
                " {} key: {}\n try -l for a list of keys".format(host, key)
            )
            exit(1)
        print(print_string)

    def add_host(self, update_dict):
        """Add a new host to the store."""
        self.dict_server.update(update_dict)

    def _get_default_dict(self):
        return_dict = {
            "structure": {
                "network": {},
                "vms": [],
                "users": [],
                "mounts": [],
                "storage": {
                    "get_info": []
                },
                "comment": "",
                "collection_time": ""
            }
        }
        return return_dict

    def get_all_host_keys(self, show):
        """Show one key in all hosts (eg. show all users)."""
        search_key = show
        host_list = self.dict_server.keys()
        missing_key = []
        for host in host_list:
            if search_key in self.dict_server[host].keys():
                print('Host: {} Key: {}'.format(host, search_key))
                print(
                    json.dumps(
                        self.dict_server[host][search_key],
                        sort_keys=True,
                        indent=4
                    )
                )
            else:
                missing_key.append(host)

        print('Hosts without the key: {}'.format(missing_key))

    def dump_dict(self, dict_to_write, json_file_path):
        """Dump the given dict to a json file."""
        db_pardir = os.path.abspath(os.path.join(
            json_file_path,
            os.pardir)
        )
        if not os.path.exists(db_pardir):
            self.logger.warning(
                'Parent directory {} dose not exist.'.format(db_pardir)
            )
            self.logger.info('creating {}'.format(db_pardir))
            os.makedirs(db_pardir)

        with open(json_file_path, 'w') as fp:
            json.dump(dict_to_write, fp, sort_keys=True, indent=4)
