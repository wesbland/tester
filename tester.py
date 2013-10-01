#!/usr/bin/env python

import getopt, sys, pprint

def usage():
    print """Usage: ./tester.py [-h] -c -i -o
    -h | --help                                Print this help output
    -c | --command-line-file {filename}        File containing the commands to execute
    -i | --input-file-format {filename}        File containing the input format
    -o | --output-file-format {filename}       File containing the output format"""

def main(argv):
    input_format = {}
    output_format = {}
    try:
        opts, args = getopt.getopt(argv, "hc:i:o:",
                ["help",
                 "command-line-file=",
                 "input-format-file=",
                 "output-format-file="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-c", "--command-line-file"):
            # Setup command line
            file = open(arg, 'r')
            command_line = file.read()
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
            pprint.pprint(input_format)
        elif opt in ("-o", "--output-format-file"):
            # Setup output format
            file = open(arg, 'r')
            output_file = file.readlines()
            first = 1
            output_format[len(output_format)] = {
                    'name': "",
                    'nomin': 0,
                    'nomax': 0,
                    'avg': 0,
                    'stddev': 0}
            for line in output_file:
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
            pprint.pprint(output_format)
        else:
            usage()
            sys.exit(2)

if __name__ == "__main__":
    main(sys.argv[1:])
