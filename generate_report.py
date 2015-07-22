from __future__ import print_function

import argparse
import datetime
from dateutil.parser import parse
import getopt
import logging
from sets import Set
import sys

logger = logging.getLogger(__name__)


class OpenStackLogAnalyzer(object):
    """Report Generator for OpenStack instance booting time"""

    def __init__(self):
        self.input_file = ''
        self.output_folder = ''

    def get_base_parser(self):
        parser = argparse.ArgumentParser(
                add_help=False,
                description='Generates OpenStack intance boot charts.')

        parser.add_argument('-h', '--help',
                action='store_true',
                help=argparse.SUPPRESS)
        parser.add_argument('-i', '--input-file',
                default='openstack.log',
                help='Accumulative log entries file.')
        parser.add_argument('-o', '--output-folder',
                required=True,
                help='Reports output folder.')
        parser.add_argument('-f', '--filename',
                required=True,
                help='Output file name.')
        parser.add_argument('-v', '--os-version',
                help='ClearLinux OS Release Version')
        parser.add_argument('-t', '--type',
                default='all',
                choices=['duration', 'interaction', 'all'],
                help='Type of graphs to generate.')

        return parser
    
    def _get_durations(self, threshold=0.0):
        with open(self.input_file, "r") as logfile:
            data = {}
            last_process = ''
            last_start = ''
            results = []
            for entry in logfile:
                if last_process != entry.split(" ")[2] and len(str(last_start)) > 0:
                    duration = parse(" ".join(entry.split(" ")[:2])) - last_start
                    if duration.total_seconds() > threshold:
                        data["process"]  = last_process[:-1]
                        data["start_time"] = last_start
                        data["duration"] = duration.total_seconds() * 1000
                              
                        results.append(data)
                        data = {}
    
                last_process = entry.split(" ")[2]
                last_start   = parse(" ".join(entry.split(" ")[:2]))
    
        return results
    
    def _group_durations(self, durations):
        last_duration = {}
        results = []
        for i, current in enumerate(durations):
            if i == 0: 
                last_duration = current
            elif last_duration["process"] == current["process"]:
                last_duration["duration"] += current["duration"]
            else:
                results.append(last_duration)
                last_duration = current
        return results
    
    def _get_os_version(self):
        with open('/usr/lib/os-release') as f:
            content = f.readlines()
        return [x.split('=')[1][:-1] for x in content if 'VERSION_ID' in x][0]
    
    def _get_summary(self, durations):
        summary = {}
        summary['os_version'] = self.os_version
        summary['total_time'] = sum ( data["duration"] for data in durations )
        summary['top_five_longest_tasks'] = sorted(durations, key=lambda data: data["duration"], reverse=True)[:5]
        return summary

    def _get_interactions(self):
        durations = self._get_durations(-1.0)
        results = Set()
        i = 0
        j = 0
        while i < len(durations):
            while durations[i]["process"].split(".")[0] == durations[j]["process"].split(".")[0]:
                j += 1
                if j >= len(durations):
                    break
            if j >= len(durations):
                break
            results.add("  %s -> %s;\n" % (durations[i]["process"].split(".")[0], durations[j]["process"].split(".")[0]))
            i = j
        return results
    
    def create_dot_file(self, filename='interation.dot'):
        interactions = self._get_interactions()
    
        with open(self.output_folder + filename, "w+") as f:
            f.write("digraph BootNovaInstance {\n")
            for interaction in interactions:
                f.write(interaction)
            f.write("}\n")
    
    def create_duration_report(self, filename='duration.html'):
        title_space = 20
    
        durations = self._group_durations(self._get_durations())
        summary = self._get_summary(durations)
    
        with open(self.output_folder + filename,"w+") as f:
            f.write("<html>\n")
            f.write("  <body>\n")
    
            # Write summary
            f.write("    <table border='1'>\n")
            f.write("      <tr>\n")
            f.write("        <td>OS Release:</td><td>%s</td>\n" % summary["os_version"])
            f.write("      </tr>\n")
            f.write("      <tr>\n")
            f.write("        <td>Total time:</td><td>%s ms</td>\n" % "{:,.2f}".format(summary["total_time"]))
            f.write("      </tr>\n")
            f.write("      <tr>\n")
            f.write("        <td colspan='2'>Top 5 longest tasks<s/td>\n")
            f.write("      </tr>\n")
            for data in summary["top_five_longest_tasks"]:
                f.write("      <tr>\n")
                f.write("        <td>%s</td><td>%s ms</td>\n" % (data["process"], "{:,.2f}".format(data["duration"])))
                f.write("      </tr>\n")
            f.write("      </tr>\n")
            f.write("    </table>\n")
    
    
            # Write results
            f.write("    <table>\n")
            time=0
            for data in durations:
                f.write("      <tr>\n")
                f.write("        <td>%s</td>\n" % data["process"])
                f.write("        <td><svg width='10000' height='20'><g>\n")
                f.write("            <rect x='%s' y='0' width='%s' height='20' style='fill:blue;stroke:black' />\n" % (time, data["duration"]))
                f.write("            <text x='%s' y='10' font-family='Verdana' font-size='10'>%s ms</text>\n" % (time + data["duration"] + title_space, "{:,.2f}".format(data["duration"])))
                f.write("        </g></svg></td>\n")
                f.write("      </tr>\n")
                time += data["duration"]
            f.write("    </table>\n")
            f.write("  </body>\n")
            f.write("</html>\n")
    
    def main(self, argv):
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)
        self.input_file = options.input_file
        self.output_folder = options.output_folder
        self.os_version = options.os_version if options.os_version else self._get_os_version()

        if options.help or not argv:
            parser.print_help()
            return 0

        if options.type in ['duration']:
            self.create_duration_report(options.filename)
        if options.type in ['interaction']:
            self.create_dot_file(options.filename)


def main():
    try:
        OpenStackLogAnalyzer().main(sys.argv[1:])
    except KeyboardInterrupt:
        print("... terminating openstack log analyzer client", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print("ERROR : " + str(e))
        logger.debug(e, exc_info=1)
        sys.exit(1)


if __name__ == "__main__":

    main()
