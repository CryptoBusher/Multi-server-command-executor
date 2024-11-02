import time
import random
import paramiko

from concurrent.futures import ThreadPoolExecutor, as_completed
from sys import stderr
from loguru import logger

from config import config, general_commands, named_commands

logger.remove()
log_format = "<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <white>{message}</white>"
logger.add(stderr, level="INFO", format=log_format)
logger.add("debug_log.log", level="DEBUG", format=log_format)


def execute_ssh_command(host, username, password, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password)

    _stdin, _stdout, _stderr = ssh.exec_command(command)
    output = _stdout.read().decode()
    error = _stderr.read().decode()

    ssh.close()

    return output, error


def execute_command_on_server(name: str, host: str, username: str, password: str, commands_list: list[str]):
    logger.info(f"Executing commands on server {name}, host: {host}")

    commands_delay_sec = config["commands_delay_sec"]
    commands_with_sleep = []
    for command in commands_list:
        commands_with_sleep.append(command)
        commands_with_sleep.append(f"sleep {random.randint(commands_delay_sec[0], commands_delay_sec[1])}")

    separator = f" && " if config["stop_on_fail"] else " ; "
    combined_command = separator.join(commands_with_sleep)

    try:
        output, error = execute_ssh_command(host, username, password, combined_command)

        logger.info(f'{name} - finished processing (see debug log for output details)')
        logger.debug(f"{name} - output:\n{output}")
        if error:
            logger.warning(f'{name} - error in output occurred (see debug log for output details)')
            logger.debug(f"{name} - error:\n{error}")

    except Exception as e:
        logger.error(f"{name} - failed to execute command: {e}")

    delay = random.randint(config["delay_sec"][0], config["delay_sec"][1])
    logger.info(f"{name} - sleeping for {delay} seconds after command execution")
    time.sleep(delay)


def main(threads: int = 5):
    with open('servers.txt', 'r') as f:
        servers = [i.strip() for i in f.readlines()]

    if len(config["execute_only_on_servers"]) > 0:
        servers = [server for server in servers if server.split('|', 1)[0] in config["execute_only_on_servers"]]

    if config["shuffle_servers"]:
        random.shuffle(servers)

    with ThreadPoolExecutor(max_workers=config.get("max_threads", threads)) as executor:
        futures = []
        for server in servers:
            name, host, username, password = server.split('|', 3)

            if name in config["skip_servers"]:
                continue

            if config["use_named_commands"]:
                try:
                    commands_list = []
                    for command in config["commands"]:
                        if command in named_commands:
                            commands_list += named_commands[command][name]
                except KeyError:
                    logger.warning(f"{name} - missing some of named commands for this server, skipping")
                    continue
            else:
                commands_list = [general_commands[name] for name in config["commands"]]

            futures.append(executor.submit(execute_command_on_server, name, host, username, password, commands_list))

        for future in as_completed(futures):
            future.result()


if __name__ == '__main__':
    main(config["threads"])
