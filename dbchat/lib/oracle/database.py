import cx_Oracle
import plotly
import webbrowser
import datetime
import plotly.graph_objs as go
from subprocess import check_output
from subprocess import CalledProcessError
from subprocess import STDOUT


class database_class(object):
    connection = None

    @classmethod
    def __init__(self):
        self.connection = None

    @classmethod
    def connect(self, config):
        host = config[1]["host"]
        user = config[1]["user"]
        password = config[1]["password"]
        sid = config[1]["sid"]
        cs = '{}/{}'.format(host, sid)
        print cs
        self.connection = cx_Oracle.connect(
            user=user, password=password,
            dsn=cs, mode=cx_Oracle.SYSDBA)

    @classmethod
    def getAAS(self, config, GUI=None):
        sqltext = """
        select mtime, round(sum(c1),2) AAS_WAIT, round(sum(c2),2) AAS_CPU, round(sum(cnt),2) AAS  from (
        select to_char(sample_time,'YYYY-MM-DD HH24') mtime, decode(session_state,'WAITING',count(*),0)/360 c1, decode(session_state,'ON CPU',count(*),0)/360 c2, count(*)/360 cnt
        from dba_hist_active_sess_history
        where dbid = 510484703
        group by  to_char(sample_time,'YYYY-MM-DD HH24'), session_state
        )
        group by mtime
        order by mtime
        """

        self.connect(config)
        cursor = self.connection.cursor()
        cursor.execute(sqltext)
        time = []
        aas_graph = []
        aas_wait = []
        aas_cpu = []
        for mtime, AAS_WAIT, AAS_CPU, AAS in cursor:
            if not GUI:
                print config[0], mtime, AAS_WAIT, AAS_CPU, AAS
            else:
                time.append(mtime)
                aas_graph.append(AAS)
                aas_wait.append(AAS_WAIT)
                aas_cpu.append(AAS_CPU)

        if GUI:
            print "GUI"
            aas_plot = go.Scatter(
                x=time,
                y=aas_graph,
                name="AAS")
            aas_plot_wait = go.Scatter(
                x=time,
                y=aas_wait,
                name="AAS WAIT")
            aas_plot_cpu = go.Scatter(
                x=time,
                y=aas_cpu,
                name="AAS CPU")

            plotly.offline.plot({
                "data": [aas_plot, aas_plot_wait, aas_plot_cpu],
                "layout": go.Layout(title="AAS")
                }, auto_open=False)

            webbrowser.get('chrome').open_new('file:////Users/mprzepiorowski/Documents/dbchat/temp-plot.html')

    @classmethod
    def getAASNOW(self, config, GUI=None):
        sqltext = """
        select cpu, waits, round((cpu+waits)/(p.value*30),2)
        from (
            select
               sum(decode(session_state,'ON CPU',1,0))    cpu,
               sum(decode(session_state,'WAITING',1,0)) waits
            from
                v$active_session_history ash
            where
                sample_time > sysdate - 30/24/60/60),
            v$parameter p
        where
            p.name='cpu_count'
        """

        self.connect(config)
        cursor = self.connection.cursor()
        cursor.execute(sqltext)
        for cpu, wait, aaspct in cursor:
            print config[0], cpu, wait, aaspct


    @classmethod
    def getHist(self, config, event_name='buffer deadlock', GUI=True):
        sqltext = """
        select * from (
        select begin_interval_time,
        ms1 - lag(ms1) over (order by begin_interval_time) ms1,
        ms2 - lag(ms2) over (order by begin_interval_time) ms2,
        ms4 - lag(ms4) over (order by begin_interval_time) ms4,
        ms8 - lag(ms8) over (order by begin_interval_time) ms8,
        ms16 - lag(ms16) over (order by begin_interval_time) ms16,
        ms32 - lag(ms32) over (order by begin_interval_time) ms32,
        ms64 - lag(ms64) over (order by begin_interval_time) ms64,
        ms128 - lag(ms128) over (order by begin_interval_time) ms128,
        ms256 - lag(ms256) over (order by begin_interval_time) ms256,
        ms512 - lag(ms512) over (order by begin_interval_time) ms512,
        ms1024 - lag(ms1024) over (order by begin_interval_time) ms1024,
        ms2048 - lag(ms2048) over (order by begin_interval_time) ms2048
        from (
        select begin_interval_time,
        max(ms1) ms1,
        max(ms2) ms2,
        max(ms4) ms4,
        max(ms8) ms8,
        max(ms16) ms16,
        max(ms32) ms32,
        max(ms64) ms64,
        max(ms128) ms128,
        max(ms256) ms256,
        max(ms512) ms512,
        max(ms1024) ms1024,
        max(ms2048) ms2048
        from (
        select s.begin_interval_time,
        decode (a.wait_time_milli,1,wait_count,0) ms1,
        decode (a.wait_time_milli,2,wait_count,0) ms2,
        decode (a.wait_time_milli,4,wait_count,0) ms4,
        decode (a.wait_time_milli,8,wait_count,0) ms8,
        decode (a.wait_time_milli,16,wait_count,0) ms16,
        decode (a.wait_time_milli,32,wait_count,0) ms32,
        decode (a.wait_time_milli,64,wait_count,0) ms64,
        decode (a.wait_time_milli,128,wait_count,0) ms128,
        decode (a.wait_time_milli,256,wait_count,0) ms256,
        decode (a.wait_time_milli,512,wait_count,0) ms512,
        decode (a.wait_time_milli,1024,wait_count,0) ms1024,
        decode (a.wait_time_milli,2048,wait_count,0) ms2048
        from DBA_HIST_EVENT_HISTOGRAM a, dba_hist_snapshot s
        where a.snap_id = s.snap_id and a.event_name like :event
        and s.dbid = 510484703 and s.dbid = a.dbid
        and a.INSTANCE_NUMBER = 1 and a.instance_number = s.instance_number
        )
        group by begin_interval_time
        order by begin_interval_time
        )
        ) where ms1 >= 0
        """

        self.connect(config)
        cursor = self.connection.cursor()
        cursor.execute(sqltext, {"event" : event_name})

        result = cursor.fetchall()

        # move to list of series
        series = zip(*result)

        time = list(series[0])
        # ms1 = list(series[1])
        # ms2 = list(series[2])

        # print time
        # print ms1
        # print ms2

        # time = [
        #     datetime.datetime(2018, 8, 4, 1, 0, 1, 649000),
        #     datetime.datetime(2018, 8, 4, 2, 0, 1, 670000),
        #     datetime.datetime(2018, 8, 4, 3, 0, 8, 635000),
        #     datetime.datetime(2018, 8, 4, 4, 0, 8, 674000),
        #     datetime.datetime(2018, 8, 4, 5, 0, 15, 480000)
        # ]
        #
        # ms1 = [
        #     None, 0, 45557, 0, 72722
        # ]
        #
        # ms2 = [
        #     None, 100, 35557, 100, 52722
        # ]

        if GUI:
            print "GUI"
            ms1 = go.Bar(
                x=time,
                y=list(series[1]),
                name="ms1")
            ms2 = go.Bar(
                x=time,
                y=list(series[2]),
                name="ms2")
            ms4 = go.Bar(
                x=time,
                y=list(series[3]),
                name="ms4")
            ms8 = go.Bar(
                x=time,
                y=list(series[4]),
                name="ms8")
            ms16 = go.Bar(
                x=time,
                y=list(series[5]),
                name="ms16")

            plotly.offline.plot({
                "data": [ms1, ms2, ms4, ms8, ms16],
                "layout": go.Layout(title=event_name, barmode='group')
                }, auto_open=False, filename='hist-plot.html')

            # webbrowser.open_new('hist-plot.html')
            webbrowser.get('chrome').open_new('file:////Users/mprzepiorowski/Documents/dbchat/hist-plot.html')


    @classmethod
    def getAWR(self, config):
        sqltext = """
        select output from
        table(dbms_workload_repository.awr_report_html(510484703,1,22525,22529))
        """

        self.connect(config)
        cursor = self.connection.cursor()
        cursor.execute(sqltext)
        result = cursor.fetchall()

        file = open('awr.html', 'w')
        file.writelines([ "%s" % x for x in result ])
        file.close()

        webbrowser.get('chrome').open_new('file:////Users/mprzepiorowski/Documents/dbchat/awr.html')



    @classmethod
    def mountddl(self, config):
        try:
            a = check_output(
                    ['/mnt/c/Users/pioro/Documents/ddlfs/target/ddlfs'],
                    stderr=STDOUT)
            print a
        except CalledProcessError as e:
            print "error %s" % e.output
