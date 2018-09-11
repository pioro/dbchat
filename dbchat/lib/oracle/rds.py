import boto3
import botocore
import time
from dbchat.lib.oracle.database import database_class
from dbchat.lib.config import convert_from_utc

class rds(database_class):

    def create(self, config):
        rds = boto3.client('rds')
        db_identifier = config[0]

        try:
            rds.create_db_instance(DBInstanceIdentifier=db_identifier,
               AllocatedStorage=200,
               DBName=db_identifier,
               Engine='oracle-se2',
               StorageType='gp2',
               LicenseModel='bring-your-own-license',
               AutoMinorVersionUpgrade=True,
               MultiAZ=False,
               MasterUsername=config[1]["user"],
               MasterUserPassword=config[1]["password"],
               DBInstanceClass='db.t2.micro')

            print 'Starting RDS instance with ID: %s' % db_identifier

        except botocore.exceptions.ClientError as e:
            if 'DBInstanceAlreadyExists' in e.message:
                print 'DB instance %s exists already, continuing to poll ...' % db_identifier
            else:
                raise


        running = True
        while running:
            response = rds.describe_db_instances(DBInstanceIdentifier=db_identifier)

            db_instances = response['DBInstances']
            if len(db_instances) != 1:
               raise Exception('Whoa cowboy! More than one DB instance returned; this should never happen')

            db_instance = db_instances[0]

            status = db_instance['DBInstanceStatus']

            print 'Last DB status: %s' % status

            time.sleep(5)
            if status == 'available':
                endpoint = db_instance['Endpoint']
                host = endpoint['Address']
                # port = endpoint['Port']

                print 'DB instance ready with host: %s' % host
                running = False

    def backup(self, config):
        rds = boto3.client('rds')
        snap = rds.describe_db_snapshots()
        snap_list = snap["DBSnapshots"]
        for s in snap_list:
            print "{:10} {:20.19} {:20.19} {:30.30} {:21}".format(
                config[0],
                str(s["SnapshotCreateTime"]),
                'N/A',
                s["DBSnapshotIdentifier"],
                'N/A'
            )
            




