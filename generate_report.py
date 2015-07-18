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

def create_report(input_file, output_file):
    durations = group_durations(get_durations(input_file))
    with open(output_file,"w+") as f:
        f.write("<html>\n")
        f.write("  <body>\n")
        f.write("    <table>\n")
        time=0
        for data in durations:
            f.write("      <tr>\n")
            f.write("        <td>%s</td>\n" % data["process"])
            f.write("        <td><svg width='10000' height='30'><g>\n")
            f.write("            <rect x='%s' y='0' width='%s' height='20' style='fill:blue;stroke:black' />\n" % (time, data["duration"]))
            f.write("            <text x='%s' y='10' font-family='Verdana' font-size='10'>%s ms</text>\n" % (time + data["duration"] + 20, data["duration"]))
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
