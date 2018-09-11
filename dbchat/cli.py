import click
import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from lib.oracle.database import database_class
from lib.oracle.virtual import virtual
from lib.oracle.physical import physical
from lib.oracle.rds import rds
from lib.config import loadconfig
from lib.config import get_list


@click.group()
def cli(obj={}):
    """
    dbchat is a DBA script helper
    """

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    debugfile = TimedRotatingFileHandler('cli.log',
                                         when="D",
                                         interval=1)
    # formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(message)s')
    formatter = logging.Formatter('[%(asctime)s:%(levelname)s:%(module)s:'
                                  '%(lineno)s - %(funcName)s()] %(message)s')
    debugfile.setFormatter(formatter)
    debugfile.setLevel(logging.DEBUG)
    logger.addHandler(debugfile)


@cli.group()
@click.pass_context
def database(ctx):
    if ctx.obj is None:
        ctx.obj = {}

    loadconfig()
    ctx.obj["database_list"] = get_list()

@database.group()
@click.pass_context
def list(ctx):
    """
    This is list command group
    There are commands like list backup or list users, etc
    """

@list.command()
@click.option('--name', help="Database name")
@click.pass_context
def backup(ctx, name):
    """This is backup list"""
    print "{:10} {:20.19} {:20.19} {:30.30} {:20}".format(
        "Database",
        "Start time",
        "End time",
        "BS name",
        'Tag')
    dblist = get_db_list(name)
    for db in dblist:
        dbobj = get_db_obj(ctx, db)
        dbobj.backup((db, ctx.obj["database_list"][db]))

# @list.command()
# @click.option('--name', help="Database name", required=True)
# @click.pass_context
# def users(ctx, name):
#     """
# 
#     """
#     print "Print backup list"
#     print ctx.obj["database_list"][name]


@database.command()
@click.option('--name', help="Database name", required=True)
@click.pass_context
def config(ctx, name):
    """
    Print configuration 
    """
    print ctx.obj["database_list"][name]


@database.command()
@click.option('--name', help="Database name", required=True)
@click.pass_context
def mountddl(ctx, name):
    """This is config"""
    print "Config"
    print ctx.obj["database_list"][name]
    dbobj = database_class()
    dbobj.mountddl((name, ctx.obj["database_list"][name]))


@database.command()
@click.option('--name', help="Database name", required=True)
@click.pass_context
def start(ctx, name):
    """This is start database command"""

    try:
        dbtype = ctx.obj["database_list"][name]["type"]

    except KeyError as e:
        print "Database name %s not found" % e.message
        sys.exit(1)

    if dbtype == "physical":
        dbobj = physical()
    elif dbtype == "virtual":
        dbobj = virtual()
    elif dbtype == "rds":
        dbobj = None
    else:
        print "Wrong type in config"
        sys.exit(1)

    dbobj.start((name, ctx.obj["database_list"][name]))
    
@database.command()
@click.option('--name', help="Database name", required=True)
@click.pass_context
def create(ctx, name):
    """This is start database command"""

    try:
        dbtype = ctx.obj["database_list"][name]["type"]

    except KeyError as e:
        print "Database name %s not found" % e.message
        sys.exit(1)

    if dbtype == "physical":
        dbobj = physical()
    elif dbtype == "virtual":
        dbobj = virtual()
    elif dbtype == "rds":
        dbobj = rds()
    else:
        print "Wrong type in config"
        sys.exit(1)

    dbobj.create((name, ctx.obj["database_list"][name]))

@database.command()
@click.option('--name', help="Database name", required=True)
@click.pass_context
def stop(ctx, name):
    """This is stop database command"""

    try:
        dbtype = ctx.obj["database_list"][name]["type"]

    except KeyError as e:
        print "Database name %s not found" % e.message
        sys.exit(1)

    if dbtype == "physical":
        dbobj = physical()
    elif dbtype == "virtual":
        dbobj = virtual()
    elif dbtype == "rds":
        dbobj = None
    else:
        print "Wrong type in config"
        sys.exit(1)

    dbobj.stop((name, ctx.obj["database_list"][name]))

@database.command()
@click.option('--name', help="Database name")
@click.pass_context
def aas(ctx, name):
    """
    Display current AAS 
    """
    dblist = get_db_list(name)
    for db in dblist:
        dbobj = get_db_obj(ctx, db)
        dbobj.getAASNOW((db, ctx.obj["database_list"][db]))

    #dbobj.getAAS((name, ctx.obj["database_list"][name]), GUI=False)

    #p.getAWR()
    #p.getAAS(True)

@database.command()
@click.option('--name', help="Database name")
@click.pass_context
def aasgui(ctx, name):
    """
    Display AAS graph from AWR 
    """
    dblist = get_db_list(name)
    for db in dblist:
        dbobj = get_db_obj(ctx, db)
        dbobj.getAAS((db, ctx.obj["database_list"][db]), GUI=True)

@database.command()
@click.option('--name', help="Database name")
@click.option('--eventname', help="Event name", required=True)
@click.pass_context
def eventhist(ctx, name, eventname):
    """
    Display event histogram from AWR 
    """
    dblist = get_db_list(name)
    for db in dblist:
        dbobj = get_db_obj(ctx, db)
        dbobj.getHist((db, ctx.obj["database_list"][db]), eventname, GUI=True)

@database.command()
@click.option('--name', help="Database name")
@click.pass_context
def awr(ctx, name):
    """
    Display an AWR
    """
    dblist = get_db_list(name)
    for db in dblist:
        dbobj = get_db_obj(ctx, db)
        dbobj.getAWR((db, ctx.obj["database_list"][db]))

def get_db_list(name):
    dblist = []
    if name and (name.lower() != 'all'):
        dblist.append(name)
    else:
        dblist = get_list().keys()

    return dblist


def get_db_obj(ctx, name):
        try:
            dbtype = ctx.obj["database_list"][name]["type"]

        except KeyError as e:
            print "Database name %s not found" % e.message
            sys.exit(1)

        if dbtype == "physical":
            dbobj = physical()
        elif dbtype == "virtual":
            dbobj = virtual()
        elif dbtype == "rds":
            dbobj = rds()
        else:
            print "Wrong type in config"
            sys.exit(1)

        return dbobj
