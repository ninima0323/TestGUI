import json
from collections import OrderedDict
import re
import random


def read_command_from_json(file_name, module_index):
    with open(file_name) as json_file:
        json_data = json.load(json_file)
        if module_index == 0:  # Zigbee HA
            if json_data["commands"]:
                list = []
                for item in json_data["commands"]:
                    cluster = item["cluster"]
                    command = item["command"]
                    payloads = item["payloads"]
                    command_string = ""
                    if cluster == "0x0006":
                        command_string = "on/off, " + str(command)
                    elif cluster == "0x0300":
                        command_string = "color, " + str(payloads[0][0])
                    elif cluster == "0x0008":
                        command_string = "level, " + str(payloads[0][0])
                    list.append(command_string)
                return list


def make_command(list, module_index, port_num):
    # file_data = OrderedDict()
    # file_data["device"] = "DongleHandler\\..\\resource\\device\\Ultra Thin Wafer.json"
    # file_data["connection"] = 0
    # commands = []
    # serial_port = port_num + 1
    # for item in list:
    #     data = re.split(", ", item)
    #     command_type = data[0]
    #     if module_index == 0:#Zigbee HA
    #         if command_type == "connect":
    #             print("connect", serial_port)
    #         elif command_type == "on/off":
    #             value = data[1]
    #             if value == "0x1":  # on
    #                 commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\on.json")
    #             elif value == "0x0":  # off
    #                 commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\off.json")
    #             elif value == "regular random":
    #                 commands.append("onoff_regular_random.json")
    #             elif value == "irregular random":
    #                 commands.append("onoff_irregular_random.json")
    #             else:
    #                 commands.append("onoff_random.json")
    #         elif command_type == "color":
    #             value = data[1]
    #             if value == "regular random":
    #                 commands.append("color_regular_random.json")
    #             elif value == "irregular random":
    #                 commands.append("color_irregular_random.json")
    #             elif value == "random":
    #                 commands.append("color_random.json")
    #             else:
    #                 commands.append("color_"+value)
    #         elif command_type == "level":
    #             value = data[1]
    #             if value == "regular random":
    #                 commands.append("level_regular_random.json")
    #             elif value == "irregular random":
    #                 commands.append("level_irregular_random.json")
    #             elif value == "random":
    #                 commands.append("level_random.json")
    #             else:
    #                 commands.append("level_"+value)
    #         elif command_type == "disconnect":
    #             print("disconnect", serial_port)
    # file_data["task_list"] = commands
    # file_data["iteration"] = 0
    # # print(json.dumps(file_data, ensure_ascii=False, indent="\t"))
    # with open('command.json', 'w', encoding='utf-8') as make_file:
    #     json.dump(file_data, make_file, ensure_ascii=False, indent="\t")
    file_data = OrderedDict()
    commands = []
    serial_port = port_num + 1
    for item in list:
        data = re.split(", ", item)
        command_type = data[0]
        if module_index == 0:  # Zigbee HA
            if command_type == "connect":
                print("connect", serial_port)
            elif command_type == "on/off":
                value = data[1]
                cluster = "0x0006"
                payloads = None
                duration = 0.5
                if value == "on":  # on
                    commands.append(get_zigbee_command(cluster, "0x01", payloads, duration))
                elif value == "off":  # off
                    commands.append(get_zigbee_command(cluster, "0x00", payloads, duration))
                elif value == "regular random":
                    # command = random.randint(0x00, 0x01)
                    command = int(data[2])
                    commands.append(get_zigbee_command(cluster, command, payloads, duration))
                elif value == "irregular random":
                    # command = random.randint(0x00, 0x01)
                    command = int(data[2])
                    commands.append(get_zigbee_command(cluster, command, payloads, duration))
                else:
                    # command = random.randint(0x00, 0x01)
                    command = int(data[2])
                    commands.append(get_zigbee_command(cluster, command, payloads, duration))
            elif command_type == "color":
                value = data[1]
                cluster = "0x0300"
                command = "0x0a"
                if value == "regular random":
                    # num = random.randint(200, 370)
                    num = int(data[2])
                    payloads = [[num, "0x21"], [0, "0x21"]]
                    commands.append(get_zigbee_command(cluster, command, payloads))
                elif value == "irregular random":
                    # num = random.randint(0x0000, 0xfeff) + 0xff00
                    num = int(data[2])
                    payloads = [[num, "0x21"], [0, "0x21"]]
                    commands.append(get_zigbee_command(cluster, command, payloads))
                elif value == "random":
                    # num = random.randint(200, 370) if random.randint(0, 1) == 0 else random.randint(0x0000,
                    #                                                                                  0xfeff) + 0xff00
                    num = int(data[2])
                    payloads = [[num, "0x21"], [0, "0x21"]]
                    commands.append(get_zigbee_command(cluster, command, payloads))
                else:
                    payloads = [[int(value), "0x21"], [0, "0x21"]]
                    commands.append(get_zigbee_command(cluster, command, payloads))
            elif command_type == "level":
                value = data[1]
                cluster = "0x0008"
                command = "0x04"
                if value == "regular random":
                    # num = random.randint(0x00, 0xfe)
                    num = int(data[2])
                    payloads = [[num, "0x20"], [0, "0x21"]]
                    commands.append(get_zigbee_command(cluster, command, payloads))
                elif value == "irregular random":
                    # num = random.randint(0x00, 0xfe) + 0xff
                    num = int(data[2])
                    payloads = [[num, "0x20"], [0, "0x21"]]
                    commands.append(get_zigbee_command(cluster, command, payloads))
                elif value == "random":
                    # num = random.randint(0x00, 0xfe) if random.randint(0, 1) == 0 else random.randint(0x00,
                    #                                                                                    0xfe) + 0xff
                    num = int(data[2])
                    payloads = [[num, "0x20"], [0, "0x21"]]
                    commands.append(get_zigbee_command(cluster, command, payloads))
                else:
                    payloads = [[int(value), "0x20"], [0, "0x21"]]
                    commands.append(get_zigbee_command(cluster, command, payloads))
            elif command_type == "disconnect":
                print("disconnect", serial_port)
    file_data["commands"] = commands
    with open('sample_command.json', 'w', encoding='utf-8') as make_file:
        json.dump(file_data, make_file, ensure_ascii=False, indent="\t")


def get_zigbee_command(cluster, command, payloads, duration=None):
    if duration:
        return {"cluster":  cluster , "command": command, "payloads": payloads, "duration": duration}
    else:
        return {"cluster":  cluster , "command": command, "payloads": payloads}
