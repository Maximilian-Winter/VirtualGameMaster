from typing import Tuple
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
