from typing import Tuple

from chat_history import ChatFormatter
from command_system import CommandSystem


@CommandSystem.command("exit")
def exit_command(vgm, *args) -> Tuple[str, bool]:
    vgm.save()
    return "Game saved. Goodbye!", True


@CommandSystem.command("save")
def save_command(vgm, *args) -> Tuple[str, bool]:
    vgm.manual_save()
    return "Game saved successfully!", False


@CommandSystem.command("view_fields")
def view_fields(vgm, *args):
    fields = vgm.template_fields
    output = "Template Fields:\n"
    output += "-----------------\n"
    for key, value in fields.items():
        output += f"{key}: {value}\n"
    return output, False


@CommandSystem.command("edit_field")
def edit_field(vgm, *args):
    if len(args) < 2:
        return "Usage: @edit_field <field_name> <new_value>", False
    field_name = args[0]
    new_value = " ".join(args[1:])
    if field_name in vgm.template_fields:
        vgm.template_fields[field_name] = new_value
        return f"Field '{field_name}' updated successfully.", False
    else:
        return f"Field '{field_name}' not found.", False


@CommandSystem.command("view_messages")
def view_messages(vgm, *args):
    messages = vgm.history.messages[-10:]  # Show last 10 messages
    output = "Recent Messages:\n"
    output += "-----------------\n"
    for msg in messages:
        output += f"ID: {msg.id}, Role: {msg.role}\n"
        output += f"Content: {msg.content[:50]}{'...' if len(msg.content) > 50 else ''}\n\n"
    return output, False


@CommandSystem.command("edit_message")
def edit_message(vgm, *args):
    if len(args) < 2:
        return "Usage: @edit_message <message_id> <new_content>", False
    try:
        message_id = int(args[0])
        new_content = " ".join(args[1:])
        if vgm.edit_message(message_id, new_content):
            return f"Message {message_id} updated successfully.", False
        else:
            return f"Message {message_id} not found.", False
    except ValueError:
        return "Invalid message ID. Please provide a number.", False


@CommandSystem.command("delete_last")
def delete_last_messages(vgm, *args):
    if len(args) != 1:
        return "Usage: @delete_last <number_of_messages>", False
    try:
        k = int(args[0])
        if k <= 0:
            return "Please provide a positive number of messages to delete.", False
        deleted = vgm.history.delete_last_messages(k)
        return f"Deleted the last {deleted} message(s).", False
    except ValueError:
        return "Invalid input. Please provide a number.", False


@CommandSystem.command("rm_all")
def delete_all_messages(vgm, *args):
    deleted = vgm.history.delete_last_messages(100000)
    return f"Deleted the last {deleted} message(s).", False


@CommandSystem.command("show_history")
def show_history(vgm, *args):
    history = vgm.get_currently_used_history()

    template = "{role}: {content}\n\n"
    role_names = {
        "assistant": "Game Master",
        "user": "Player"
    }
    formatter = ChatFormatter(template, role_names)

    output = "History:\n"
    if len(history) > 0:
        output += formatter.format_messages(history)
    else:
        output += "History is empty.\n"

    return output, False
