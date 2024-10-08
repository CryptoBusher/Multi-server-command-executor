import time
import random
from sys import stderr

import paramiko
from loguru import logger

from config import config, general_commands, named_commands

logger.remove()
log_format = "<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <white>{message}</white>"
logger.add(stderr, level="INFO", format=log_format)
logger.add("debug_log.log", level="DEBUG", format=log_format)


def execute_command_on_server(name: str, host: str, username: str, password: str, commands_list: list[str],
                              stop_on_fail: bool = True, delay_sec: list[int] | None = None):
    if delay_sec is None:
        delay_sec = [0, 0]

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for command in commands_list:
        try:
            ssh.connect(hostname=host, username=username, password=password)

            stdin, stdout, _stderr = ssh.exec_command(command)
            output = stdout.read().decode()
            error = _stderr.read().decode()

            logger.info(f"{name} - output:\n{output}")
            time.sleep(random.randint(1, 3))

            if error:
                logger.error(f"{name} - output:\n{error}")
                if stop_on_fail:
                    logger.warning(f"{name} - stopping commands execution")
                    break

        except Exception as e:
            logger.error(f"{name} - failed to execute command: {e}")
            if stop_on_fail:
                logger.warning(f"{name} - stopping commands execution")
                break

        delay = random.randint(delay_sec[0], delay_sec[1])
        time.sleep(delay)

    ssh.close()


def main():
    with open('servers.txt', 'r') as f:
        servers = [i.strip() for i in f.readlines()]

    if config["shuffle_servers"]:
        random.shuffle(servers)

    for server in servers:
        name, host, username, password = server.split('|', 3)

        if name in config["skip_servers"]:
            continue

        delay = random.randint(config["delay_sec"][0], config["delay_sec"][1])
        if delay > 0:
            logger.info(f"{name} - waiting {delay} seconds")
            time.sleep(delay)

        if config["use_named_commands"]:
            try:
                commands_list = []
                for command in config["commands"]:
                    if command in named_commands:
                        commands_list += named_commands[command][name]
            except KeyError:
                logger.error(f"{name} - missing some of named commands for this server, skipping")
                continue
        else:
            commands_list = [general_commands[name] for name in config["commands"]]

        execute_command_on_server(name, host, username, password, commands_list, config["stop_on_fail"])


if __name__ == '__main__':
    main()
