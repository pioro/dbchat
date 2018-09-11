import boto3
import botocore
import time


def main():

    rds = boto3.client('rds')

    db_identifier = 'test'


#    try:
#        rds.create_db_instance(DBInstanceIdentifier=db_identifier,
#            AllocatedStorage=200,
#            DBName='test',
#            Engine='postgres',
#            StorageType='gp2',
#            AutoMinorVersionUpgrade=True,
#            MultiAZ=False,
#            MasterUsername='root',
#            MasterUserPassword='rootroot',
#            DBInstanceClass='db.t2.micro')
#
#        print 'Starting RDS instance with ID: %s' % db_identifier
#
#    except botocore.exceptions.ClientError as e:
#        if 'DBInstanceAlreadyExists' in e.message:
#            print 'DB instance %s exists already, continuing to poll ...' % db_identifier
#        else:
#            raise
#
#
#    running = True
#    while running:
#        response = rds.describe_db_instances(DBInstanceIdentifier=db_identifier)
#
#        db_instances = response['DBInstances']
#        if len(db_instances) != 1:
#            raise Exception('Whoa cowboy! More than one DB instance returned; this should never happen')
#
#        db_instance = db_instances[0]
#
#        status = db_instance['DBInstanceStatus']
#
#        print 'Last DB status: %s' % status
#
#        time.sleep(5)
#        if status == 'available':
#            endpoint = db_instance['Endpoint']
#            host = endpoint['Address']
#            # port = endpoint['Port']
#
#            print 'DB instance ready with host: %s' % host
#            running = False
#


    try:
        response = rds.stop_db_instance(
            DBInstanceIdentifier=db_identifier
        )

    except botocore.exceptions.ClientError as e:
        print "Instance stopped %s" % e.message

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
        if status == 'stopped':
            endpoint = db_instance['Endpoint']
            host = endpoint['Address']
            # port = endpoint['Port']

            print 'DB instance stopped' 
            running = False

    

    try:
        response = rds.start_db_instance(
            DBInstanceIdentifier=db_identifier
        )

    except botocore.exceptions.ClientError as e:
        print "Instance stopped %s" % e.message


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





if __name__ == '__main__':
    main()

