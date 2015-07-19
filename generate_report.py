import sys
import getopt
import datetime

from dateutil.parser import parse

def get_durations(filename):
    with open(filename, "r") as logfile:
        data = {}
        last_process = ''
        last_start = ''
        results = []
        for entry in logfile:
            if last_process != entry.split(" ")[2] and len(str(last_start)) > 0:
                duration = parse(" ".join(entry.split(" ")[:2])) - last_start
                if duration.total_seconds() != 0.0:
                    data["process"]  = last_process[:-1]
                    data["start_time"] = last_start
                    data["duration"] = duration.total_seconds() * 1000
                          
                    results.append(data)
                    data = {}

            last_process = entry.split(" ")[2]
            last_start   = parse(" ".join(entry.split(" ")[:2]))

    return results

def group_durations(durations):
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

def get_os_version():
    with open('/usr/lib/os-release') as f:
        content = f.readlines()
    return [x.split('=')[1][:-1] for x in content if 'VERSION_ID' in x][0]

def get_summary(durations):
    summary = {}
    summary['os_version'] = get_os_version()
    summary['total_time'] = sum ( data["duration"] for data in durations )
    summary['top_five_longest_tasks'] = sorted(durations, key=lambda data: data["duration"], reverse=True)[:5]
    return summary

def create_report(input_file, output_file):
    title_space = 20

    durations = group_durations(get_durations(input_file))
    summary = get_summary(durations)

    with open(output_file,"w+") as f:
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


def print_help():
    print 'usage: generate_report.py -i <inputfile>'


def main(argv):
    input_file=''
    output_file=''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["input=","output="])
    except getopt.error, msg:
        print msg
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg
    create_report(input_file, output_file)

if __name__ == "__main__":
    main(sys.argv[1:])
