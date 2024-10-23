config = {
    "run_async": True,
    "use_named_commands": False,                        # режим персональных команд, которые определены в словаре "named_commands"
    "commands": [                                       # названия команд из словаря "commands" ниже (или из словаря "named_commands", если включен соответствующий режим)
        "run_node"
    ],
    "stop_on_fail": True,                               # прервать выполнение команд при неудачном исполнении предыдущей
    "delay_sec": [0, 200],                              # задержка перед выполнением (мин, макс), секунды
    "commands_delay_sec": [2, 5],                       # задержка между последовательными командами на сервере (мин, макс), секунды
    "shuffle_servers": True,                            # перемешать порядок серверов
    "skip_servers": [                                   # список названий серверов, которые надо пропустить
        "1",
        "10"
    ]
}

general_commands = {
    "open_port": "sudo ufw allow 17690/tcp",

    "run_node": """
    docker run -d \
      --env-file /root/validator.env \
      --name elixir \
      -p 17690:17690 \
      elixirprotocol/validator:v3
    """,

    "stop_node": "docker kill elixir && docker rm elixir",

    "docker_pull": "docker pull elixirprotocol/validator:v3"
}

named_commands = {
    "run_node": {
        "1": [
            "pwd",
            "ls"
        ],
        "2": [
            "ls",
            "pwd"
        ]
    }
}