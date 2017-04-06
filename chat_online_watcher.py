#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import os
import json
import time
import sys
import logging
import atexit
from realplexor import Dklab_Realplexor, Dklab_Realplexor_Exception


def daemonize(pidfile):
    """Deamonize class. UNIX double fork mechanism."""
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError as err:
        sys.stderr.write('fork #1 failed: {0}\n'.format(err))
        sys.exit(1)

    # decouple from parent environment
    os.chdir('/')
    os.setsid()
    os.umask(0)

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent
            sys.exit(0)
    except OSError as err:
        sys.stderr.write('fork #2 failed: {0}\n'.format(err))
        sys.exit(1)

    def delpid():
        os.remove(pidfile)
    # write pidfile
    atexit.register(delpid)

    pid = str(os.getpid())
    with open(pidfile, 'w+') as f:
        f.write(pid + '\n')


def watch_status(config, log, daemon):
    print(daemon)
    assert os.path.isfile(config) is True, 'Config {0} does not exists Please copy conf/chat_online.sample.json to {0} and edit it'.format(config)
    logging.basicConfig(filename=log, level=logging.DEBUG, format='%(levelname)s %(asctime)s %(message)s')

    with open(config, 'r+') as settings_file:
        try:
            watch_settings = json.load(settings_file)
        except ValueError:
            watch_settings = {}
    if daemon:
        daemonize('/var/run/dklab_realplexor_chat_online_watcher.pid')
    realplexor_connections = []
    for namespace, settings in watch_settings.items():
        connection = Dklab_Realplexor(settings['host'], settings['port'], namespace, settings.get('identifier', 'identifier'))
        setattr(connection, 'pos', 0)
        setattr(connection, 'id_prefix', settings.get('id_prefix', 'id_'))
        setattr(connection, 'online_channel', settings['online_channel'])
        setattr(connection, 'site', settings['site'])
        realplexor_connections.append(connection)

    while True:
        for connection in realplexor_connections:
            try:
                for event in connection.cmdWatch(connection.pos, [connection.id_prefix]):
                    try:
                        user_id = event['id'].split(connection.id_prefix)[1]
                    except IndexError:
                        user_id = event['id']
                    logging.debug("{0} user {1} is {2}".format(connection.site, user_id, event['event']))
                    connection.pos = event['pos']
                    if event['event'] == 'FAKE':
                        continue
                    connection.send({connection.online_channel}, json.dumps([{
                        'status': event['event'], 'id': user_id
                    }]))
            except Dklab_Realplexor_Exception as e:
                logging.error(str(e))

        time.sleep(2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
       Watches online/offline user status at Dklab realpexor chat\n
        Usage example:
        ''')
    default_config = os.path.join(os.path.dirname(__file__), 'conf/chat_online.json')
    default_log = os.path.join(os.path.dirname(__file__), 'chat_online_watcher.log')
    parser.add_argument('--config', type=str, metavar='config', nargs=1,
                        help='Chat online watcher config path', required=False, default=[default_config])
    parser.add_argument('--log', type=str, metavar='log', nargs=1,
                        help='Chat online watcher log path', required=False, default=[default_log])
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    params = parser.parse_args()
    watch_status(params.config[0], params.log[0], params.daemon)