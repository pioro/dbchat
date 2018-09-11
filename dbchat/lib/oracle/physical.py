from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.executor.playbook_executor import PlaybookExecutor
from dbchat.lib.oracle.database import database_class




class physical(database_class):

    def backup(self, config):
        sqltext = """
        SELECT s.start_time, s.completion_time, handle, tag
        FROM   V$BACKUP_PIECE P, V$BACKUP_SET S
        WHERE  P.SET_STAMP = S.SET_STAMP
        AND    P.SET_COUNT = S.SET_COUNT
        AND    P.STATUS = 'A'
        AND    S.BACKUP_TYPE = 'D'
        AND    exists (select 1 from V$BACKUP_FILES
                       where bs_count = s.SET_COUNT
                       and file_type = 'DATAFILE')
        """
        self.connect(config)
        cursor = self.connection.cursor()
        cursor.execute(sqltext)
        for start_time, completion_time, handle, tag in cursor:
            print "{:10} {:20.19} {:20.19} {:30.30} {:21}".format(
                config[0],
                str(start_time),
                str(completion_time),
                handle,
                tag)


    def start(self, config):
        self.run_ansible('./dbchat/start.yml')


    def stop(self, config):
        self.run_ansible('./dbchat/stop.yml')


    def run_ansible(self, playbook, config):

        ansible_host = config[1]["host"]
        # run ansible playbook

        loader = DataLoader()

        # inventory = Inventory(loader=loader, variable_manager=variable_manager,host_list='/home/felixc/ansible/hosts')
        inventory = InventoryManager(loader=loader, sources=['/etc/ansible/hosts'])
        inventory.subset(ansible_host)
        variable_manager = VariableManager(loader=loader, inventory=inventory)
        variable_manager.extra_vars = {
            'oh': '/u01/app/oracle/12.1.0.2/db1',
            'sid': config[1]["sid"],
            'mode': 'immediate'
        }

        passwords={}

        Options = namedtuple('Options',
                             ['connection',
                              'remote_user',
                              'ask_sudo_pass',
                              'verbosity',
                              'ack_pass',
                              'module_path',
                              'forks',
                              'become',
                              'become_method',
                              'become_user',
                              'check',
                              'listhosts',
                              'listtasks',
                              'listtags',
                              'syntax',
                              'sudo_user',
                              'sudo',
                              'diff'])

        options = Options(
            connection='smart',
            remote_user=None,
            ack_pass=None,
            sudo_user=None,
            forks=5,
            sudo=None,
            ask_sudo_pass=False,
            verbosity=5,
            module_path=None,
            become=None,
            become_method=None,
            become_user=None,
            check=False,
            diff=False,
            listhosts=None,
            listtasks=None,
            listtags=None,
            syntax=None)

        playbook = PlaybookExecutor(playbooks=[playbook],inventory=inventory,
                      variable_manager=variable_manager,
                      loader=loader,options=options,passwords=passwords)
        a = playbook.run()
