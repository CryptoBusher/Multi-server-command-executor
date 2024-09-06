config = {
    "commands": [                                       # названия команд из словаря "commands" ниже
        "stop_node",
        "docker_pull",
        "run_node"
    ],
    "stop_on_fail": True,                               # прервать выполнение команд при неудачном исполнении предыдущей
    "delay_sec": [0, 200],                              # задержка перед выполнением (мин, макс), секунды
    "skip_servers": [                                   # список названий серверов, которые надо пропустить
        "1",
        "10"
    ]
}

commands = {
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
