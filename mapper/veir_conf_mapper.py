""" creates a mapped veir_conf.env environment file in current directory based on openstack environment show output and an existing veir_conf.env file used as a template

    usage:
        python PR_mapper.py <stack_id> <existing veir_conf env file>

    example:
        python PR_mapper.py 0507cf58-97c1-4f42-a8c6-7078bbd9063d ../veir_conf.env

    output:
        'veir_conf.env_mapped' created in current directory


"""

import os
import sys
import ruamel.yaml


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
    stack_show_data = f.read()

stack_show_data = ruamel.yaml.round_trip_load(
    stack_show_data, preserve_quotes=True)


def change_value(dictionary, key, value):
    for k, v in dictionary.items():
        if k == key:
            if not isinstance(v, dict) and not isinstance(v, list):
                dictionary[key] = value
            else:
                change_value(v, key, value)


def map_dicts(dict1, dict2):
    for k, v in dict1.items():
        for key, value in dict2.items():
            if k == key:
                if not isinstance(value, dict) and not isinstance(value, list):
                    change_value(
                        dict1, key, value)
                elif isinstance(value, dict):
                    for keyy in value:
                        # print(keyy)
                        # sys.exit(1)
                        try:
                            keyy = int(keyy)
                            change_value(
                                dict1[key], keyy, value[str(keyy)])
                        except (KeyError, ValueError) as e:
                            change_value(
                                dict1[key], keyy, value[keyy])


def map_list_of_dicts(list1, list2):
    for k, v in list1.items():
        for key, value in list2.items():
            if k == key:
                if not isinstance(value, dict) and not isinstance(value, list):
                    change_value(
                        list1, key, value)
                elif isinstance(value, dict):
                    for keyy in value:
                        if not isinstance(value[keyy], list):
                            change_value(
                                list1[key], keyy, value[keyy])
                        else:
                            list1[key][keyy] = value[keyy]
                else:
                    list1[key] = value


for k, v in env_file_data['parameters'].items():
    for key, value in stack_show_data['parameters'].items():
        if k == key:
            if not isinstance(value, dict) and not isinstance(value, list):
                change_value(
                    env_file_data['parameters'], key, value)
            elif isinstance(value, list):
                for i in range(len(env_file_data['parameters'][key])):
                    map_list_of_dicts(
                        env_file_data['parameters'][key][i], stack_show_data['parameters'][key][i])

map_dicts(env_file_data['parameters']['routes'],
          stack_show_data['parameters']['routes'])


for k, v in env_file_data['parameters']['ss7'].items():
    for key, value in stack_show_data['parameters']['ss7'].items():
        if k == key:
            if not isinstance(value, dict) and not isinstance(value, list):
                change_value(
                    env_file_data['parameters']['ss7'], key, value)
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    if not isinstance(v, dict):
                        env_file_data['parameters']['ss7'][key] = list(
                            value)
                    else:
                        for keyy, valuee in v.items():
                            if not isinstance(valuee, dict) and not isinstance(valuee, list):
                                for i in range(len(env_file_data['parameters']['ss7'][key])):
                                    map_list_of_dicts(env_file_data['parameters']['ss7'][key]
                                                      [i], stack_show_data['parameters']['ss7'][key][i])
            else:
                for keyy, valuee in v.items():
                    if isinstance(valuee, list):
                        for i in range(len(env_file_data['parameters']['ss7'][key][keyy])):
                            map_list_of_dicts(
                                env_file_data['parameters']['ss7'][key][keyy][i], stack_show_data['parameters']['ss7'][key][keyy][i])
                map_dicts(v, value)


for k, v in env_file_data['parameters']['pn_config'].items():
    for key, value in stack_show_data['parameters']['pn_config'].items():
        if k == key:
            if not isinstance(value, dict) and not isinstance(value, list):
                change_value(
                    env_file_data['parameters']['pn_config'], key, value)
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    if not isinstance(v, dict):
                        env_file_data['parameters']['pn_config'][key] = list(
                            value)
                    else:
                        for keyy, valuee in v.items():
                            if not isinstance(valuee, dict) and not isinstance(valuee, list):
                                for i in range(len(env_file_data['parameters']['pn_config'][key])):
                                    map_list_of_dicts(env_file_data['parameters']['pn_config'][key]
                                                      [i], stack_show_data['parameters']['pn_config'][key][i])

for k, v in env_file_data['parameter_defaults'].items():
    for key, value in stack_show_data['parameter_defaults'].items():
        if k == key:
            if not isinstance(value, dict):
                change_value(env_file_data['parameter_defaults'], key, value)
            else:
                for keyy in value:
                    change_value(
                        env_file_data['parameter_defaults'][key], keyy, value[keyy])


with open(new_env_file, 'w') as f:
    ruamel.yaml.round_trip_dump(
        env_file_data, f)

print("'" + new_env_file + "'" + ' created in current directory.')

os.system('rm -f {}'.format(stack_show_temp))
