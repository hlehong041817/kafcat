#!/usr/bin/env python

"""
Read Kafka topic contents and output it to the stdout.
"""

import getopt
import kafka
import os.path
import sys


def usage(exitcode = 1):
    """
    Show usage info and exit.
    """
    argv0 = os.path.basename(sys.argv[0])
    sys.stdout.write(
        'Usage: ' + argv0 + ' [options] topicname\n'
        ' Options:\n'
        '  --host Host   Kafka node hostname. Default is "localhost";\n'
        '  --port Port   Kafka node port number. Default is 9092;\n'
        '  -b            extract from the beginning;\n'
        '  -f            output appended data as the topic grows.\n')
    sys.exit(exitcode)


if __name__ == '__main__':
    # Parse command line options
    try:
        cmd_opts, cmd_args = getopt.getopt(
            sys.argv[1:], 'bf', ['host=', 'port='])
        cmd_opts = dict(cmd_opts)
    except getopt.GetoptError as exc:
        sys.stderr.write('Error: ' + str(exc) + '\n')
        usage()
    if len(cmd_args) != 1:
        usage()
    consumer = None
    try:
        # connect to Kafka
        host = cmd_opts.get('--host', 'localhost')
        port = int(cmd_opts.get('--port', '9092'))
        client = kafka.KafkaClient(host + ':' + str(port))
        # Create consumer object
        consumer = kafka.SimpleConsumer(
            client, 'kafcat', cmd_args[0],
            iter_timeout = None if '-f' in cmd_opts else 0.5)
        if '-b' in cmd_opts:
            # seek very first message
            consumer.seek(0, 0)
            consumer.commit()
        # start consuming
        for message in consumer:
            sys.stdout.write(message.message.value + '\n')
        # save current position for the future use
        consumer.commit()
    except KeyboardInterrupt:
        if consumer is not None:
            # save current position for the future use
            consumer.commit()
        sys.exit(130)
