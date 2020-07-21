import os

def isValidRange(val):
    if 0 < val < 65279:
        return True
    else:
        return False

PADDING_FOR_TIME = 0.2
PADDING_FOR_VALUE = 50 

def analyze_result(log_path):
    with open(log_path, 'r') as f:
        lines = f.readlines()[1:]
        result_list = []
        line_read = []
        line_command = []
        for line in lines:
            origin_line = line.split('\n')[0]
            line = line.split('\n')[0].split(';')
            if line[1] == "COMMAND_TASK":
                line_command = line
            elif line[1] == "READ_ATTRIBUTE_TASK":
                line_read = line
                if line_command != []:
                    if 'COLOR_CTRL' == line_command[2]: # color ctrl
                        input_cmd = line_command[3]
                        input_val = int(line_command[4].split(',')[0][2:])
                        input_duration = float(line_command[4].split(',')[2][2:]) * 0.1
                        interval = float(line_command[5])
                        output_val = int(line_read[5])
                
                        if input_val == output_val : # OK
                            result_list.append(line_command.append("OK"))
                            result_list.append(line_read.append("OK"))
                        else:
                            if interval > input_duration: # enough to transit color or temperature to the target point
                                if (interval - input_duration) <= PADDING_FOR_TIME:
                                    e = "Error : The interval value may be short compared to the transition time."
                                    line_command.append(e)
                                    line_read.append(e)
                                    result_list.append(line_command)
                                    result_list.append(line_read)
                                elif (abs(output_val - input_val) <= PADDING_FOR_VALUE):
                                    e = "Error : The distance between the input value and the output value is too far for the given transition time."
                                    line_command.append(e)
                                    line_read.append(e)
                                    result_list.append(line_command)
                                    result_list.append(line_read)
                            else:   # short to transit color or temperature to the target point
                                e = "Error : The interval value may be short compared to the transition time."
                                line_command.append(e)
                                line_read.append(e)
                                result_list.append(line_command)
                                result_list.append(line_read)
                    elif 'LVL_CTRL' == line_command[2]: # color ctrl
                        input_cmd = line_command[3]
                        input_val = int(line_command[4].split(',')[0][2:])
                        input_duration = float(line_command[4].split(',')[2][2:]) * 0.1
                        interval = float(line_command[5])
                        output_val = int(line_read[5])
                
                        if input_val == output_val : # OK
                            line_command.append("OK")
                            line_read.append("OK")
                            result_list.append(line_command)
                            result_list.append(line_read)
                        else:
                            if interval > input_duration: # enough to transit color or temperature to the target point
                                if (interval - input_duration) <= PADDING_FOR_TIME:
                                    e = "Error : The interval value may be short compared to the transition time."
                                    line_command.append(e)
                                    line_read.append(e)
                                    result_list.append(line_command)
                                    result_list.append(line_read)
                                elif (abs(output_val - input_val) <= PADDING_FOR_VALUE): # change to abs(previous output - current input)
                                    e= "Error : The distance between the input value and the output value is too far for the given transition time."
                                    line_command.append(e)
                                    line_read.append(e)
                                    result_list.append(line_command)
                                    result_list.append(line_read)
                            else:   # short to transit color or temperature to the target point
                                e = "Error : The interval value may be short compared to the transition time."
                                line_command.append(e)
                                line_read.append(e)
                                result_list.append(line_command)
                                result_list.append(line_read)
                    elif 'ON_OFF' == line_command[2]:
                        input_cmd = line_command[3]
                        input_val = "True" if input_cmd == "ON" else "False"  
                        input_duration = 0.1
                        interval = float(line_command[5])
                        output_val = line_read[5]
              
                        if input_val == output_val : # OK
                            line_command.append("OK")
                            line_read.append("OK")
                            result_list.append(line_command)
                            result_list.append(line_read)
                        else:
                            if interval > input_duration: # enough to transit color or temperature to the target point
                                if (interval - input_duration) <= PADDING_FOR_TIME:
                                    e = "Error : The interval value may be short compared to the transition time."
                                    line_command.append(e)
                                    line_read.append(e)
                                    result_list.append(line_command)
                                    result_list.append(line_read)
                                elif (abs(output_val - input_val) <= PADDING_FOR_VALUE):
                                    e =  "Error : The distance between the input value and the output value is too far for the given transition time."
                                    line_command.append(e)
                                    line_read.append(e)
                                    result_list.append(line_command)
                                    result_list.append(line_read)
                            else:   # short to transit color or temperature to the target point
                                e = "Error : The interval value may be short compared to the transition time."
                                line_command.append(e)
                                line_read.append(e)
                                result_list.append(line_command)
                                result_list.append(line_read)
        return result_list
        