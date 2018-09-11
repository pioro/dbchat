import sys
import re
from delphixpy.v1_9_1.web.source import source
from delphixpy.v1_9_1.web.database import database
from delphixpy.v1_9_1.web.snapshot import snapshot
from delphixpy.exceptions import RequestError
from dbchat.lib.DxEngine import DxEngine
from dbchat.lib.oracle.database import database_class
from dbchat.lib.config import convert_from_utc

class virtual(database_class):

    def backup(self, config):
        engine = DxEngine()
        # load Engine config
        engine.get_config('./dxtools.conf')
        engine.connect(config[1]["delphix"])
        try:
            listdb = database.get_all(engine.get_engine())
            vdb = [x for x in listdb if x.name == config[0]]

            snapshots = snapshot.get_all(
                engine.get_engine(),
                database=vdb[0].reference)

            for snap in snapshots:
                range = snapshot.timeflow_range(
                    engine.get_engine(),
                    snap.reference)

                print "{:10} {:20.19} {:20.19} {:30.30} {:20}".format(
                    config[0],
                    convert_from_utc(snap.creation_time, snap.timezone.split(',')[0], None),
                    convert_from_utc(range.start_point.timestamp, snap.timezone.split(',')[0], None),
                    snap.name,
                    'N/A')

        except RequestError as e:
            self.__logger.error("Can't read database set. Exiting")
            self.__logger.debug(e)
            sys.exit(1)

    def start(self, config):
        engine = DxEngine()
        # load Engine config
        engine.get_config('./dxtools.conf')
        engine.connect(config[1]["delphix"])
        self.__sources = {}
        try:

            for sourceref in source.get_all(engine.get_engine()):
                if (re.match(r'.*StagingSource', sourceref.type)):
                    self.__sources[sourceref.reference] = sourceref
                else:
                    self.__sources[sourceref.container] = sourceref

            listdb = database.get_all(engine.get_engine())
            vdb = [x for x in listdb if x.name == config[0]]
            source.start(
                engine.get_engine(),
                self.__sources[vdb[0].reference].reference)

        except RequestError as e:
            self.__logger.error("Can't start database. Exiting")
            self.__logger.debug(e)
            sys.exit(1)

    def stop(self, config):
        engine = DxEngine()
        # load Engine config
        engine.get_config('./dxtools.conf')
        engine.connect(config[1]["delphix"])
        self.__sources = {}
        try:

            for sourceref in source.get_all(engine.get_engine()):
                if (re.match(r'.*StagingSource', sourceref.type)):
                    self.__sources[sourceref.reference] = sourceref
                else:
                    self.__sources[sourceref.container] = sourceref

            listdb = database.get_all(engine.get_engine())
            vdb = [x for x in listdb if x.name == config[0]]
            source.stop(
                engine.get_engine(),
                self.__sources[vdb[0].reference].reference)

        except RequestError as e:
            self.__logger.error("Can't stop database. Exiting")
            self.__logger.debug(e)
            sys.exit(1)
