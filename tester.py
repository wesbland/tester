#!/usr/bin/env python

import getopt, sys, pprint, re, subprocess, numpy

command_format = {}
input_format = {}
output_format = {}
data = {}

def main(argv):
    parse_args(argv)

    run_tests()

    process_results()

def usage():
    print """Usage: ./tester.py [-h] -c -i -o
    -h | --help                                Print this help output
    -c | --command-file {filename}             File containing the commands to execute
    -i | --input-file-format {filename}        File containing the input format
    -o | --output-file-format {filename}       File containing the output format"""

def parse_args(argv):
    try:
        opts, args = getopt.getopt(argv, "hc:i:o:",
                ["help",
                 "command-file=",
                 "input-format-file=",
                 "output-format-file="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-c", "--command-file"):
            # Setup command line
            file = open(arg, 'r')
            line_num = 1
            command_file = file.readlines()
            for line in command_file:
                if line_num == 1:
                    command_format['repetitions'] = int(line)
                elif line_num == len(command_file):
                    command_format['command'] = line
                else:
                    var_spec = line.split()
                    command_format[line_num-2] = {
                            'start': float(var_spec[0]),
                            'stop': float(var_spec[1]),
                            'stride': float(var_spec[2]),
                            'cur_val': float(var_spec[0])}
                line_num += 1
        elif opt in ("-i", "--input-format-file"):
            # Setup input format
            file = open(arg, 'r')
            input_file = file.readlines()
            for line in input_file:
                input_format[len(input_format)] = {
                        'name': line.strip(),
                        'min': sys.maxint,
                        'max': -sys.maxint-1,
                        'total': 0,
                        'num': 0}
                if line.strip() != "ignore":
                    data[line.strip()] = {}
        elif opt in ("-o", "--output-format-file"):
            # Setup output format
            file = open(arg, 'r')
            output_file = file.readlines()
            for line in output_file:
                first = 1
                output_format[len(output_format)] = {
                        'name': "",
                        'nomin': 0,
                        'nomax': 0,
                        'avg': 0,
                        'stddev': 0}
                for word in line.split():
                    if first == 1:
                        output_format[len(output_format)-1]['name'] = word
                        first = 0
                        continue
                    if word == "nomin":
                        output_format[len(output_format)-1]['nomin'] = 1
                    elif word == "nomax":
                        output_format[len(output_format)-1]['nomax'] = 1
                    elif word == "avg":
                        output_format[len(output_format)-1]['avg'] = 1
                    elif word == "stddev":
                        output_format[len(output_format)-1]['stddev'] = 1
                    else:
                        print "Invalid output format specification: " + word
                        sys.exit(2)
        else:
            usage()
            sys.exit(2)

def run_tests():
    # This will get determined on the fly by the stride for each variable
    done = 0
    while not done:
        curr_command = command_format['command']
        while True:
            match = re.search('%(\d)', curr_command)
            if match == None:
                break
            curr_command = re.sub(match.group(0), str(command_format[int(match.group(1))]['cur_val']), curr_command)
        for rep in xrange(command_format['repetitions']):
            process = subprocess.Popen(curr_command.split(), stdout=subprocess.PIPE)
            result = process.communicate()[0]
            var_num = 0
            for var in result.split():
                if input_format[var_num]['name'] == "ignore":
                    continue
                if command_format[var_num]['cur_val'] not in data[input_format[var_num]['name']]:
                    data[input_format[var_num]['name']][command_format[var_num]['cur_val']] = {'raw': []}
                data[input_format[var_num]['name']][command_format[var_num]['cur_val']]['raw'].append(float(var))
                var_num += 1
        for var in command_format:
            if var == "repetitions" or var == "command":
                continue
            command_format[var]['cur_val'] = command_format[var]['cur_val'] + command_format[var]['stride']
            if command_format[var]['cur_val'] > command_format[var]['stop']:
                done = 1
                break

def process_results():
    for num in output_format:
        if output_format[num]['name'] == "ignore":
            continue
        var_data = data[input_format[num]['name']]
        for val in sorted(var_data, key=var_data.get):
            print str(val) + "",
            if output_format[num]['nomin'] == 1:
                var_data[val]['raw'].remove(min(var_data[val]['raw']))
            if output_format[num]['nomax'] == 1:
                var_data[val]['raw'].remove(max(var_data[val]['raw']))
            if output_format[num]['avg'] == 1:
                var_data[val]['avg'] = numpy.mean(var_data[val]['raw'])
                print "\t" + str(var_data[val]['avg']) + "",
            if output_format[num]['stddev'] == 1:
                var_data[val]['stddev'] = numpy.std(var_data[val]['raw'])
                print "\t" + str(var_data[val]['stddev']) + "",
            print

if __name__ == "__main__":
    main(sys.argv[1:])
