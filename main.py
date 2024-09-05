import time
import random
from sys import stderr

import paramiko
from loguru import logger

from config import config, commands


logger.remove()
log_format = "<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <white>{message}</white>"
logger.add(stderr, level="INFO", format=log_format)


def execute_command_on_server(name: str, host: str, username: str, password: str, command: str):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname=host, username=username, password=password)

        stdin, stdout, _stderr = ssh.exec_command(command)
        output = stdout.read().decode()
        error = _stderr.read().decode()

        logger.info(f"{name} - output:\n{output}")
        if error:
            logger.error(f"{name} - output:\n{error}")

    except Exception as e:
        logger.error(f"{name} - failed to execute command: {e}")

    finally:
        ssh.close()


def main():
    with open('servers.txt', 'r') as f:
        servers = [i.strip() for i in f.readlines()]

    for server in servers:
        name, host, username, password = server.split('|', 3)

        if name in config["skip_servers"]:
            continue

        delay = random.randint(config["delay_sec"][0], config["delay_sec"][1])
        if delay > 0:
            logger.info(f"{name} - waiting {delay} seconds")
            time.sleep(delay)

        execute_command_on_server(name, host, username, password, commands[config["command"]])


if __name__ == '__main__':
    main()
