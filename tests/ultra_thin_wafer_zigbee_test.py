from context import DongleHandler
from DongleHandler import *
import logging

# This is basic test on Ultra Thin Wafer by Samsung Electronics.
if __name__ == "__main__":

    # for logging
    logging.basicConfig(level=logging.DEBUG)

    # Device Initialization
    ultra_thin_wafer = Device("Ultra Thin Wafer", 0x8e89bed6, 0xFFFE88571D018E53, 8)

    # Making Cmd & commandRoutine
    # off_command    = Cmd(ON_OFF_CLUSTER, ON_OFF_OFF_CMD, None, 0.5)
    # on_command     = Cmd(ON_OFF_CLUSTER, ON_OFF_ON_CMD, None, 0.5)

    # low_command    = Cmd(LVL_CTRL_CLUSTER, LVL_CTRL_MV_TO_LVL_ONOFF_CMD, [(0x02, TYPES.UINT8), (6, TYPES.UINT16)], 0.61)
    # high_command   = Cmd(LVL_CTRL_CLUSTER, LVL_CTRL_MV_TO_LVL_ONOFF_CMD, [(0xFD, TYPES.UINT8), (6, TYPES.UINT16)], 0.61)

    # sw_light_command = Cmd(COLOR_CTRL_CLUSTER, COLOR_CTRL_MV_TO_COLOR_TEMP_CMD, [(370, TYPES.UINT16), (5, TYPES.UINT16)], 0.5)
    # dl_light_command = Cmd(COLOR_CTRL_CLUSTER, COLOR_CTRL_MV_TO_COLOR_TEMP_CMD, [(200, TYPES.UINT16), (5, TYPES.UINT16)], 0.5)

    lvl_mv_cmd = Cmd(LVL_CTRL_CLUSTER, LVL_CTRL_MOVE_ONOFF_CMD, [(0x00, TYPES.ENUM8), (0x1F, TYPES.UINT8)], 0.51)
    lvl_remain_time_read_attr = ReadAttr(LVL_CTRL_CLUSTER, LVL_CTRL_REMAIN_TIME_ATTR, 0.51)

    command_list = []
    command_list.append(lvl_mv_cmd)
    command_list.append(lvl_remain_time_read_attr)
    command_list.append(lvl_remain_time_read_attr)
    command_list.append(lvl_remain_time_read_attr)
    command_list.append(lvl_remain_time_read_attr)
    command_list.append(lvl_remain_time_read_attr)
    command_list.append(lvl_remain_time_read_attr)
    command_list.append(lvl_remain_time_read_attr)
    command_list.append(lvl_remain_time_read_attr)

    simple_routine = TaskRoutine(ultra_thin_wafer, ZIGBEE_CONNECTION, command_list, 1)

    # start routine
    simple_routine.start_routine()