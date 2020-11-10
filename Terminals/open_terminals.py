"""
    extracts from targets.txt file the to-be-spawned terminals titles, local commands and expect commands, creates a new file containing only the expect
    commands, opens the terminals with the appropriate titles and commands given and then deletes the expect commands file.
"""
import os
import time


OPEN_TERMINAL_TEMPLATE = 'gnome-terminal {geometry} --working-directory={working_dir} --tab-with-profile=notitlechange  -t {title} -- bash -c "expect /home/zaasnav/scripts/Terminals/commands.txt ; exec bash"'

# string from file containing all the titles, commands and expect commands.
with open('targets.txt', 'r') as f:
    targets = f.read()


def extract_titles(targets):
    """
        Returns a list containing all the titles for the terminals.
    """
    targets = targets.split('-----')
    targets = [target.strip() for target in targets]
    titles = []

    for target in targets:
        target = target.split('\n')
        title = target[0]
        titles.append(title)

    return titles


def extract_geometries(targets):
    targets = targets.split('-----')
    geometries = []
    for target in targets:
        target = target.strip().split('\n')[1]
        if '--geometry' in target:
            geometries.append(target)

    return geometries


def extract_expect_commands(targets):
    """
        Returns a list containing all the commands for each terminal.
    """
    targets = targets.split('-----')
    expect_commands_list = []
    for target in targets:
        target = target.strip()
        expect_commands = target.split('\n')[1:]
        for command in expect_commands:
            if ('spawn ' not in command and 'interact' not in command and 'expect ' not in command and 'send ' not in command):
                expect_commands.remove(command)

        expect_commands_list.append(expect_commands)

    expect_commands_strings = []
    for item in expect_commands_list:
        item = '\n'.join(item)
        expect_commands_strings.append(item)

    return expect_commands_strings


def extract_working_dirs(targets):
    """
        Returns a list containing all the initial working directories for the terminals.
    """
    targets = targets.split('-----')
    dir_list = []
    for target in targets:
        line = '\n'.join(target.strip().split('\n')[1:2]).split('\n')[0]
        # print(line)
        if ('spawn ' not in line and 'interact' not in line and 'expect ' not in line and 'send ' not in line):
            dir_list.append(line)
        else:
            dir_list.append('$home')

    return dir_list


def open_terminal(title, geometry, expect_commands, working_dir):
    with open('commands.txt', 'w') as f:
        f.write(expect_commands)

    command = OPEN_TERMINAL_TEMPLATE.format(
        geometry=geometry, title=title, working_dir=working_dir)
    os.system(command)


titles = extract_titles(targets)
geometries = extract_geometries(targets)
expect_commands_list = extract_expect_commands(targets)
working_dirs = extract_working_dirs(targets)


for title, expect_commands, working_dir, geometry in zip(titles, expect_commands_list, working_dirs, geometries):
    open_terminal(title, geometry, expect_commands, working_dir)
    time.sleep(0.5)


os.system('rm -f commands.txt')
