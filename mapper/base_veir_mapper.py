""" creates a mapped base_veir environment file in current directory based on openstack environment show output and an existing base_veir.env file used as a template

    usage:
        python PR_mapper.py <stack_id> <existing base_veir env file>

    example:
        python PR_mapper.py 0507cf58-97c1-4f42-a8c6-7078bbd9063d ../base_veir.env

    output:
        'base_veir.env_mapped' created in current directory


"""
import os
import sys
import ruamel


stack_id = sys.argv[1]
env_file = sys.argv[2]
new_env_file = os.path.basename(env_file) + '_mapped'
stack_show_temp = 'stack_show_temp.txt'

os.system(
    'openstack stack environment show -f yaml {} > {}'.format(stack_id, stack_show_temp))

with open(env_file, 'r') as f:
    env_file_data = f.read()

env_file_data = ruamel.yaml.round_trip_load(
    env_file_data, preserve_quotes=True)


with open(stack_show_temp, 'r') as f:
    stack_show_data = f.read()  # yaml.load(f)

stack_show_data = ruamel.yaml.round_trip_load(
    stack_show_data, preserve_quotes=True)


def change_value(dictionary, key, value):
    for k, v in dictionary.items():
        if k == key:
            if not isinstance(v, dict) and not isinstance(v, list):
                dictionary[key] = value
            else:
                change_value(v, key, value)


for k, v in env_file_data['parameters'].items():
    for key, value in stack_show_data['parameters'].items():
        if k == key:
            if not isinstance(value, dict):
                change_value(env_file_data['parameters'], key, value)
            else:
                for keyy in value:
                    try:
                        keyy = int(keyy)
                        change_value(
                            env_file_data['parameters'][key], keyy, value[str(keyy)])
                    except (KeyError, ValueError) as e:
                        change_value(
                            env_file_data['parameters'][key], keyy, value[keyy])


for k, v in env_file_data['parameters']['eir_networks'].items():
    for key, value in stack_show_data['parameters']['eir_networks'].items():
        if k == key:
            if not isinstance(value, dict):
                change_value(env_file_data['parameters']
                             ['eir_networks'], key, value)
            else:
                for keyy in dict(value):
                    try:
                        keyy = int(keyy)
                        change_value(
                            env_file_data['parameters']['eir_networks'][key], keyy, value[str(keyy)])
                    except (KeyError, ValueError) as e:
                        change_value(
                            env_file_data['parameters']['eir_networks'][key], keyy, value[keyy])


with open(new_env_file, 'w') as f:
    ruamel.yaml.round_trip_dump(
        env_file_data, f)

print("'" + new_env_file + "'" + ' created in current directory.')
os.system('rm -f {}'.format(stack_show_temp))
