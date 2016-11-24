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

"""Merge the meta data form multiple nodes into one document."""

# @Author: Uwe Schilling, schilling@hlrs.de
# @COMPANY: HLRS, University of Stuttgart
# @Date: 2016-11-22


import os
import json
import click
import logging


def dump_dict(dict, json_file_path):
    """Dump the given dict to a json file."""
    with open(json_file_path, 'w') as fp:
        json.dump(dict, fp)


def get_logger():
    """Setup the global logger."""
    # log setup
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)
    logger.debug('Logger setup complete. Start Program ... ')
    return logger


@click.command()
@click.option(
    '--input_path',
    type=click.Path(exists=True),
    help='the path to the directory containing the json files',
    required=True)
@click.option(
    '--out_file',
    type=click.STRING,
    help='the file where the merged json gets written to',
    required=True)
@click.option(
    '--name',
    type=click.STRING,
    help='name of the json root',
    required=True)
def main(input_path, name, out_file):
    """
    Script to merges json files for the node meta data information.

    The annotation will parse the input with click and build the needed
    arguments.
    --name          name of the root for the new document
    --input_path    path to the json files
    --out_file      the file where the new document is written to
    """
    merge_dict = {name: {}}  # setup
    logger = get_logger()
    # iterate over path
    for file in os.listdir(input_path):
        logger.info('Reading %s' % file)
        # found a json file
        path_to_node_json = str('%s/%s' % (input_path, file))

        # test if exist
        if os.path.exists(path_to_node_json) and file.endswith('.json'):
            # read the content
            with open(path_to_node_json, 'r') as json_file:
                tmp_dict = json.load(json_file)
                merge_dict[name].update(tmp_dict)

    # write the merged json to file
    dump_dict(merge_dict, out_file)


if __name__ == '__main__':
    """Start now!"""
    main()
