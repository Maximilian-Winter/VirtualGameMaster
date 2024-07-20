from typing import Callable, Dict, Tuple


class CommandSystem:
    commands: Dict[str, Callable] = {}

    @classmethod
    def command(cls, name: str):
        def decorator(func: Callable):
            cls.commands[name.lower()] = func
            return func

        return decorator

    @classmethod
    def handle_command(cls, vgm, command: str, *args) -> Tuple[str, bool]:
        command = command.lower()
        if command in cls.commands:
            return cls.commands[command](vgm, *args)
        return f"Unknown command: {command}", False
