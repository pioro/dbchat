#
# Copyright 2017 by Delphix
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# pylint: disable=W0401,W0622


import json
import sys
import httplib
import socket
import logging
from delphixpy.v1_9_1.delphix_engine import DelphixEngine
from delphixpy.exceptions import RequestError
from delphixpy.exceptions import HttpError
from delphixpy.v1_9_1.web.service.time import time


class DxEngine(object):
    """
    Class to get the configuration and returns an Delphix authentication
    object
    """

    def __init__(self):
        self.__logger = logging.getLogger()
        self.__logger.debug("creating object")
        self.__engineobject = None
        self.__connected = False
        self.__dlpx_engines = {}

    def get_all(self):
        return self.__dlpx_engines.keys()

    def get_engine(self):
        return self.__engineobject

    def getenginename(self):
        return self.__enginename

    def getlastjob(self):
        return self.__engineobject.last_job

    def connect(self, engine_name):
        """
        connect to Delphix Engine specified by engine name
        """
        self.__logger.debug("connecting to %s" % engine_name)
        try:
            engine = self.__dlpx_engines[engine_name]
            self.__enginename = engine_name
            self.serversess(engine['ip_address'],
                            engine['username'],
                            engine['password'])
            return self.__connected

        except KeyError:
            self.__logger.error("Can't find engine name: %s in configuration"
                                "file" % engine_name)
            sys.exit(1)

    def get_config(self, config_file_path='./dxtools.conf'):
        """
        This method reads in the dxtools.conf file

        config_file_path: path to the configuration file.
                          Default: ./dxtools.conf
        """
        self.__logger.debug("reading config file %s"
                            % config_file_path)

        # First test to see that the file is there and we can open it
        try:
            config_file = open(config_file_path).read()

            # Now parse the file contents as json and turn them into a
            # python dictionary, throw an error if it isn't proper json
            config = json.loads(config_file)

        except IOError:
            self.__logger.error('Was unable to open %s  Please '
                                'check the path and permissions, and try '
                                'again.\n' % (config_file_path))
            sys.exit(1)

        except (ValueError, TypeError) as e:
            self.__logger.error('Was unable to read %s as json. '
                                'Please check if the file is in a json format'
                                ' and try again.\n' % (config_file_path))
            self.__logger.debug(e)
            sys.exit(1)

        # Create a dictionary of engines (removing the data node from the
        # dxtools.json, for easier parsing)
        for each in config['data']:
            self.__dlpx_engines[each['hostname']] = each

    def serversess(self, f_engine_address, f_engine_username,
                   f_engine_password, f_engine_namespace='DOMAIN'):
        """
        Method to setup the session with the Virtualization Engine

        f_engine_address: The Virtualization Engine's address (IP/DNS Name)
        f_engine_username: Username to authenticate
        f_engine_password: User's password
        f_engine_namespace: Namespace to use for this session. Default: DOMAIN
        """
        self.__logger.debug("connecting to Delphix Engine "
                            "address %s username %s namespace %s"
                            % (f_engine_address, f_engine_username,
                               f_engine_namespace))
        try:
            self.__connected = False
            self.__engineobject = DelphixEngine(f_engine_address,
                                                f_engine_username,
                                                f_engine_password,
                                                f_engine_namespace)
            self.__logger.debug("setting timezone")
            timeobj = time.get(self.__engineobject)
            self.__engine_time_zone = timeobj.system_time_zone
            self.__connected = True
        except HttpError as e:
            if (e.status == 401):
                self.__logger.error('Wrong password or username for engine %s'
                                    % f_engine_address)
            else:
                self.__logger.error('An error occurred while authenticating'
                                    ' to %s:\n' % f_engine_address)
                self.__logger.debug(e.status)
            sys.exit(1)

        except RequestError as e:
            self.__logger.error(e)
            sys.exit(1)

        except (httplib.HTTPException, socket.error) as ex:
            self.__logger.error("Issue when connecting to engine %s (IP %s) "
                                "- %s" % (self.__enginename,
                                          f_engine_address,
                                          str(ex)))
            self.__logger.debug(ex)
