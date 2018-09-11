import click

@click.group()
def dbchat(obj={}):
    """
    dbchat is a DBA helper
    """


@dbchat.group()
def database():
    """
    This is database group
    """
    print "This is command from datbase group"

@dbchat.command()
def file():
    """
    This is a file command
    """
    print "This is a file command"

@database.command()
def list():
    """
    This is a list command
    """
    print "This is a command from list command"


if __name__ == "__main__":
    dbchat()
