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

    low_command    = Cmd(LVL_CTRL_CLUSTER, LVL_CTRL_MV_TO_LVL_ONOFF_CMD, [(0x00, TYPES.UINT8), (6, TYPES.UINT16)], 0.51)
    # high_command   = Cmd(LVL_CTRL_CLUSTER, LVL_CTRL_MV_TO_LVL_ONOFF_CMD, [(0xFD, TYPES.UINT8), (6, TYPES.UINT16)], 0.61)

    # sw_light_command = Cmd(COLOR_CTRL_CLUSTER, COLOR_CTRL_MV_TO_COLOR_TEMP_CMD, [(370, TYPES.UINT16), (5, TYPES.UINT16)], 0.5)
    # dl_light_command = Cmd(COLOR_CTRL_CLUSTER, COLOR_CTRL_MV_TO_COLOR_TEMP_CMD, [(200, TYPES.UINT16), (5, TYPES.UINT16)], 0.5)

    lvl_move_cmd = Cmd(LVL_CTRL_CLUSTER, LVL_CTRL_MOVE_ONOFF_CMD, [(0x02, TYPES.ENUM8), (0xFF, TYPES.UINT8)], 0.51)
    lvl_step_cmd = Cmd(LVL_CTRL_CLUSTER, LVL_CTRL_STEP_ONOFF_CMD, [(0x00, TYPES.ENUM8), (0xFF, TYPES.UINT8), (0xFFFE, TYPES.UINT16)], 0.51)
    lvl_curr_lvl_attr = ReadAttr(LVL_CTRL_CLUSTER, LVL_CTRL_CURR_LVL_ATTR, 0.51)
    lvl_remain_time_attr = ReadAttr(LVL_CTRL_CLUSTER, LVL_CTRL_REMAIN_TIME_ATTR, 0.51)

    mv_to_color_cmd = Cmd(COLOR_CTRL_CLUSTER, COLOR_CTRL_MV_TO_COLOR_CMD, [(0x0000, TYPES.UINT16), (0x0000, TYPES.UINT16), (0xFFFF, TYPES.UINT16)], 0.51)
    read_color_x_attr = ReadAttr(COLOR_CTRL_CLUSTER, COLOR_CTRL_CURR_X_ATTR, 0.51)
    read_color_y_attr = ReadAttr(COLOR_CTRL_CLUSTER, COLOR_CTRL_CURR_Y_ATTR, 0.51)
    read_remain_attr = ReadAttr(COLOR_CTRL_CLUSTER, COLOR_CTRL_REMAINING_TIME_ATTR, 0.51)

    move_color_cmd = Cmd(COLOR_CTRL_CLUSTER, COLOR_CTRL_MOVE_COLOR_CMD, [(0xFFFF, TYPES.SINT16), (0xFFFF, TYPES.SINT16)], 0.51)

    step_color_cmd = Cmd(COLOR_CTRL_CLUSTER, COLOR_CTRL_STEP_COLOR_CMD, [(-0xFFFF, TYPES.SINT16), (-0xFFFF, TYPES.SINT16), (0x0000, TYPES.UINT16)], 0.51)

    move_color_temp_cmd = Cmd(COLOR_CTRL_CLUSTER, COLOR_CTRL_MV_COLOR_TEMP_CMD, [(0x03, TYPES.MAP8), (0xffff, TYPES.UINT16), (0xffff, TYPES.UINT16), (0xffff, TYPES.UINT16)], 0.51)
    read_color_temp_attr = ReadAttr(COLOR_CTRL_CLUSTER, COLOR_CTRL_COLOR_TEMP_MIRED_ATTR, 0.51)
    read_min_color_temp_attr = ReadAttr(COLOR_CTRL_CLUSTER, COLOR_CTRL_COLOR_TEMP_MIN_MIRED_ATTR, 0.51)
    read_max_color_temp_attr = ReadAttr(COLOR_CTRL_CLUSTER, COLOR_CTRL_COLOR_TEMP_MAX_MIRED_ATTR, 0.51)

    # step_color_temp_cmd = Cmd(COLOR_CTRL_CLUSTER, COLOR_CTRL_STEP_COLOR_TEMP_CMD, [(0x00, TYPES.MAP8), ()])
    read_color_mode_attr = ReadAttr(COLOR_CTRL_CLUSTER, COLOR_CTRL_COLOR_MODE_ATTR, 0.51)

    task_list = []
    task_list.append(read_color_mode_attr)
    
    simple_routine = TaskRoutine(ultra_thin_wafer, ZIGBEE_CONNECTION, task_list, 1)

    # start routine
    simple_routine.start_routine()