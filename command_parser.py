import json
from collections import OrderedDict
import random


def read_command_from_json(file_name, module_index):
    with open(file_name) as json_file:
        json_data = json.load(json_file)
        list = []
        if module_index == 0:  # Zigbee HA
            if "iteration" in json_data: #routine 의 경우
                list.append("routine, " + str(json_data["iteration"]))
                for item in json_data["task_list"]:
                    command_type = item.split("\\")[-1].split("_")
                    if command_type[0] == "on.json" or command_type[0] == "off.json":
                        list.append("on/off, " + command_type[0].split(".")[0])
                    else:
                        list.append(command_type[0] + ", " + command_type[-1].split(".")[0])
                return list
            elif "commands" in json_data: #single command 의 경우
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


def make_command(list, module_index, port_num, routine_count=-1):
    file_data = OrderedDict()
    if routine_count > 0: #routine 의 경우
        file_data["device"] = "DongleHandler\\..\\resource\\device\\Ultra Thin Wafer.json"
        file_data["connection"] = 0
        commands = []
        serial_port = port_num + 1
        for item in list:
            data = item.split(", ")
            command_type = data[0]
            if module_index == 0:  # Zigbee HA
                if command_type == "connect":
                    print("connect", serial_port)
                elif command_type == "on/off":
                    value = data[1]
                    if value == "on" or value == "0x01":  # on
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\on.json")
                    elif value == "off" or value == "0x00":  # off
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\off.json")
                    elif value == "regular random":
                        commands.append("onoff_regular_random.json")
                    elif value == "irregular random":
                        commands.append("onoff_irregular_random.json")
                    else:
                        commands.append("onoff_random.json")
                elif command_type == "color":
                    value = data[1]
                    if value == "regular random":
                        commands.append("color_regular_random.json")
                    elif value == "irregular random":
                        commands.append("color_irregular_random.json")
                    elif value == "random":
                        commands.append("color_random.json")
                    elif value == "cw":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\color_cw.json")
                    elif value == "dl":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\color_dl.json")
                    elif value == "nw":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\color_nw.json")
                    elif value == "sw":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\color_sw.json")
                    elif value == "ww":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\color_ww.json")
                elif command_type == "level":
                    value = data[1]
                    if value == "regular random":
                        commands.append("level_regular_random.json")
                    elif value == "irregular random":
                        commands.append("level_irregular_random.json")
                    elif value == "random":
                        commands.append("level_random.json")
                    elif value == "10":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\level_10.json")
                    elif value == "50":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\level_50.json")
                    elif value == "100":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\level_100.json")
                elif command_type == "disconnect":
                    print("disconnect", serial_port)
        file_data["task_list"] = commands
        file_data["iteration"] = routine_count
        with open('command_routine.json', 'w', encoding='utf-8') as make_file:
            json.dump(file_data, make_file, ensure_ascii=False, indent="\t")
    else: #single command 의 경우
        commands = []
        serial_port = port_num + 1
        for item in list:
            data = item.split(", ")
            command_type = data[0]
            if module_index == 0:  # Zigbee HA
                if command_type == "connect":
                    print("connect", serial_port)
                elif command_type == "on/off":
                    value = data[1]
                    cluster = "0x0006"
                    payloads = None
                    duration = 0.5
                    if value == "on" or value == "0x01":  # on
                        commands.append(get_zigbee_command(cluster, "0x01", payloads, duration))
                    elif value == "off" or value == "0x00":  # off
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
