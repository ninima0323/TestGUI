import json
from collections import OrderedDict
import random
from constants import *

zigbee_str_to_attr = {
    ON_OFF_CLUSTER: {"ON_OFF_ONOFF_ATTR": ON_OFF_ONOFF_ATTR},
    COLOR_CTRL_CLUSTER: {"COLOR_CTRL_CURR_HUE_ATTR": COLOR_CTRL_CURR_HUE_ATTR,
                         "COLOR_CTRL_CURR_SAT_ATTR": COLOR_CTRL_CURR_SAT_ATTR,
                         "COLOR_CTRL_REMAINING_TIME_ATTR": COLOR_CTRL_REMAINING_TIME_ATTR,
                         "COLOR_CTRL_CURR_X_ATTR": COLOR_CTRL_CURR_X_ATTR,
                         "COLOR_CTRL_CURR_Y_ATTR": COLOR_CTRL_CURR_Y_ATTR,
                         "COLOR_CTRL_COLOR_TEMP_MIRED_ATTR": COLOR_CTRL_COLOR_TEMP_MIRED_ATTR,
                         "COLOR_CTRL_COLOR_MODE_ATTR": COLOR_CTRL_COLOR_MODE_ATTR,
                         "COLOR_CTRL_ENHANCED_COLOR_MODE_ATTR": COLOR_CTRL_ENHANCED_COLOR_MODE_ATTR,
                         "COLOR_CTRL_COLOR_CAPABILITY_ATTR": COLOR_CTRL_COLOR_CAPABILITY_ATTR,
                         "COLOR_CTRL_COLOR_TEMP_MIN_MIRED_ATTR": COLOR_CTRL_COLOR_TEMP_MIN_MIRED_ATTR,
                         "COLOR_CTRL_COLOR_TEMP_MAX_MIRED_ATTR": COLOR_CTRL_COLOR_TEMP_MAX_MIRED_ATTR},
    LVL_CTRL_CLUSTER: {"LVL_CTRL_CURR_LVL_ATTR": LVL_CTRL_CURR_LVL_ATTR,
                       "LVL_CTRL_REMAIN_TIME_ATTR": LVL_CTRL_REMAIN_TIME_ATTR,
                       "LVL_CTRL_ONOFF_TRANS_TIME_ATTR": LVL_CTRL_ONOFF_TRANS_TIME_ATTR,
                       "LVL_CTRL_ON_LEVEL_ATTR": LVL_CTRL_ON_LEVEL_ATTR}}

zigbee_attr_to_str = {
    ON_OFF_CLUSTER: {ON_OFF_ONOFF_ATTR: "ON_OFF_ONOFF_ATTR"},
    COLOR_CTRL_CLUSTER: {COLOR_CTRL_CURR_HUE_ATTR: "COLOR_CTRL_CURR_HUE_ATTR",
                         COLOR_CTRL_CURR_SAT_ATTR: "COLOR_CTRL_CURR_SAT_ATTR",
                         COLOR_CTRL_REMAINING_TIME_ATTR: "COLOR_CTRL_REMAINING_TIME_ATTR",
                         COLOR_CTRL_CURR_X_ATTR: "COLOR_CTRL_CURR_X_ATTR",
                         COLOR_CTRL_CURR_Y_ATTR: "COLOR_CTRL_CURR_Y_ATTR",
                         COLOR_CTRL_COLOR_TEMP_MIRED_ATTR: "COLOR_CTRL_COLOR_TEMP_MIRED_ATTR",
                         COLOR_CTRL_COLOR_MODE_ATTR: "COLOR_CTRL_COLOR_MODE_ATTR",
                         COLOR_CTRL_ENHANCED_COLOR_MODE_ATTR: "COLOR_CTRL_ENHANCED_COLOR_MODE_ATTR",
                         COLOR_CTRL_COLOR_CAPABILITY_ATTR: "COLOR_CTRL_COLOR_CAPABILITY_ATTR",
                         COLOR_CTRL_COLOR_TEMP_MIN_MIRED_ATTR: "COLOR_CTRL_COLOR_TEMP_MIN_MIRED_ATTR",
                         COLOR_CTRL_COLOR_TEMP_MAX_MIRED_ATTR: "COLOR_CTRL_COLOR_TEMP_MAX_MIRED_ATTR"},
    LVL_CTRL_CLUSTER: {LVL_CTRL_CURR_LVL_ATTR: "LVL_CTRL_CURR_LVL_ATTR",
                       LVL_CTRL_REMAIN_TIME_ATTR: "LVL_CTRL_REMAIN_TIME_ATTR",
                       LVL_CTRL_ONOFF_TRANS_TIME_ATTR: "LVL_CTRL_ONOFF_TRANS_TIME_ATTR",
                       LVL_CTRL_ON_LEVEL_ATTR: "LVL_CTRL_ON_LEVEL_ATTR"}}


def read_command_from_json(file_name, module_index):
    with open(file_name) as json_file:
        json_data = json.load(json_file)
        list = []
        if module_index == 0:  # Zigbee HA
            if "iteration" in json_data:  # routine 의 경우
                list.append("routine, " + str(json_data["iteration"]))
                for item in json_data["task_list"]:
                    command_type = item.split("\\")[-1].split("_")
                    if command_type[0] == "on.json" or command_type[0] == "off.json":
                        list.append("on/off, " + command_type[0].split(".")[0])
                    else:
                        list.append(command_type[0] + ", " + command_type[-1].split(".")[0])
            elif "tasks" in json_data:  # single command 의 경우
                for item in json_data["tasks"]:
                    task_kind = item["task_kind"]
                    cluster = item["cluster"]
                    command_string = ""
                    if cluster == ON_OFF_CLUSTER:
                        if task_kind == 0:
                            command = item["command"]
                            command_string = "on/off, " + str(command)
                        else:
                            attr_id = item["attr_id"]
                            command_string = "read attribute, " + zigbee_attr_to_str[cluster][attr_id]
                    elif cluster == COLOR_CTRL_CLUSTER:
                        if task_kind == 0:
                            payloads = item["payloads"]
                            command_string = "color, " + str(payloads[0][0])
                        else:
                            attr_id = item["attr_id"]
                            command_string = "read attribute, " + zigbee_attr_to_str[cluster][attr_id]
                    elif cluster == LVL_CTRL_CLUSTER:
                        if task_kind == 0:
                            payloads = item["payloads"]
                            command_string = "level, " + str(payloads[0][0])
                        else:
                            attr_id = item["attr_id"]
                            command_string = "read attribute, " + zigbee_attr_to_str[cluster][attr_id]
                    list.append(command_string)
        return list


def make_command(list, module_index, port_num, routine_count=-1, make_file=False):
    if routine_count > 0:  # routine 의 경우
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
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\onoff_regular_random.json")
                    elif value == "irregular random":
                        commands.append(
                            "DongleHandler\\..\\resource\\command_type\\Zigbee\\onoff_irregular_random.json")
                    else:
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\onoff_random.json")
                elif command_type == "color":
                    value = data[1]
                    if value == "regular random":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\color_regular_random.json")
                    elif value == "irregular random":
                        commands.append(
                            "DongleHandler\\..\\resource\\command_type\\Zigbee\\color_irregular_random.json")
                    elif value == "random":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\color_random.json")
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
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\level_regular_random.json")
                    elif value == "irregular random":
                        commands.append(
                            "DongleHandler\\..\\resource\\command_type\\Zigbee\\level_irregular_random.json")
                    elif value == "random":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\level_random.json")
                    elif value == "10":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\level_10.json")
                    elif value == "50":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\level_50.json")
                    elif value == "100":
                        commands.append("DongleHandler\\..\\resource\\command_type\\Zigbee\\level_100.json")
                elif command_type == "disconnect":
                    print("disconnect", serial_port)
        file_data = OrderedDict()
        file_data["device"] = "DongleHandler\\..\\resource\\device\\Ultra Thin Wafer.json"
        file_data["connection"] = 0
        file_data["task_list"] = commands
        file_data["iteration"] = routine_count
        if make_file:
            with open('command_routine.json', 'w', encoding='utf-8') as make_file:
                json.dump(file_data, make_file, ensure_ascii=False, indent="\t")
        return file_data
    else:  # single command 와 read attribute의 경우
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
                    cluster = ON_OFF_CLUSTER
                    payloads = None
                    duration = 0.5
                    if value == "on" or value == "0x01":  # on
                        commands.append(get_zigbee_command(cluster, 0x01, payloads, duration))
                    elif value == "off" or value == "0x00":  # off
                        commands.append(get_zigbee_command(cluster, 0x00, payloads, duration))
                    elif value == "regular random":
                        command = int(data[2])
                        commands.append(get_zigbee_command(cluster, command, payloads, duration))
                    elif value == "irregular random":
                        command = int(data[2])
                        commands.append(get_zigbee_command(cluster, command, payloads, duration))
                    else:
                        command = int(data[2])
                        commands.append(get_zigbee_command(cluster, command, payloads, duration))
                elif command_type == "color":
                    value = data[1]
                    cluster = COLOR_CTRL_CLUSTER
                    command = 0x0a
                    duration = 0.5
                    if value == "regular random":
                        num = int(data[2])
                        payloads = [[num, 0x21], [0, 0x21]]
                        commands.append(get_zigbee_command(cluster, command, payloads, duration))
                    elif value == "irregular random":
                        num = int(data[2])
                        payloads = [[num, 0x21], [0, 0x21]]
                        commands.append(get_zigbee_command(cluster, command, payloads, duration))
                    elif value == "random":
                        num = int(data[2])
                        payloads = [[num, 0x21], [0, 0x21]]
                        commands.append(get_zigbee_command(cluster, command, payloads, duration))
                    else:
                        payloads = [[int(value), 0x21], [0, 0x21]]
                        commands.append(get_zigbee_command(cluster, command, payloads, duration))
                elif command_type == "level":
                    value = data[1]
                    cluster = LVL_CTRL_CLUSTER
                    command = 0x04
                    duration = 0.5
                    if value == "regular random":
                        num = int(data[2])
                        payloads = [[num, 0x20], [0, 0x21]]
                        commands.append(get_zigbee_command(cluster, command, payloads, duration))
                    elif value == "irregular random":
                        num = int(data[2])
                        payloads = [[num, 0x20], [0, 0x21]]
                        commands.append(get_zigbee_command(cluster, command, payloads, duration))
                    elif value == "random":
                        num = int(data[2])
                        payloads = [[num, 0x20], [0, 0x21]]
                        commands.append(get_zigbee_command(cluster, command, payloads, duration))
                    else:
                        payloads = [[int(value), 0x20], [0, 0x21]]
                        commands.append(get_zigbee_command(cluster, command, payloads, duration))
                elif command_type == "disconnect":
                    print("disconnect", serial_port)
                elif command_type == "read attribute":
                    task_kind = 1
                    attribute = data[1]
                    duration = 0.51
                    if "ONOFF" in attribute:
                        cluster = ON_OFF_CLUSTER
                        attr_id = zigbee_str_to_attr[cluster][attribute]
                        command = get_zigbee_command(cluster, attr_id=attr_id, duration=duration, task_kind=task_kind)
                        commands.append(command)
                    elif "COLOR" in attribute:
                        cluster = COLOR_CTRL_CLUSTER
                        attr_id = zigbee_str_to_attr[cluster][attribute]
                        command = get_zigbee_command(cluster, attr_id=attr_id, duration=duration, task_kind=task_kind)
                        commands.append(command)
                    elif "LVL" in attribute:
                        cluster = LVL_CTRL_CLUSTER
                        attr_id = zigbee_str_to_attr[cluster][attribute]
                        command = get_zigbee_command(cluster, attr_id=attr_id, duration=duration, task_kind=task_kind)
                        commands.append(command)
        file_data = OrderedDict()
        file_data["tasks"] = commands
        if make_file:
            with open('sample_command.json', 'w', encoding='utf-8') as make_file:
                json.dump(file_data, make_file, ensure_ascii=False, indent="\t")
        return file_data


def get_zigbee_command(cluster, command=None, payloads=None, duration=None, attr_id=None, task_kind=0):
    if task_kind == 0:
        if duration:
            return {"task_kind": task_kind, "cluster": cluster, "command": command, "payloads": payloads,
                    "duration": duration}
        else:
            return {"task_kind": task_kind, "cluster": cluster, "command": command, "payloads": payloads}
    else:
        return {"task_kind": task_kind, "cluster": cluster, "attr_id": attr_id, "duration": duration}
