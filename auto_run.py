import time
import os
from datetime import datetime
import sys


def get_time():
    now = datetime.now()
    return now.strftime("%H:%M:%S")


def error_tret(file_path, confige_file_path, command):
    with open(confige_file_path, 'r') as file:
        lines = file.readlines()
        modified_lines = []
        for line in lines:
            if 'margin' in line:
                line = 'margin               5'
            modified_lines.append(line)
    with open(confige_file_path, 'w') as file:
        file.writelines(modified_lines)
    
    print('margin has been chate, rerun')
    os.system(command)
    read_log(file_path, confige_file_path, command)


def update_center():
    os.system('cd 000_eq && /home/sxc/miniconda3/bin/python 000.2_updateCenters.py')
    print('All the *.in files updated for the Geometrical route!')


def get_folder_list(path):
    folder_list = [folder for folder in os.listdir(path) if os.path.isdir(folder)]
    return folder_list


def get_config_list(path):
    config_list = [file for file in os.listdir(path) if file.endswith('.conf') and 'extend' not in file]
    return config_list


def read_log(file_path, confige_file_path, command):
    file_name = file_path.split('/')[-1].split('_')[0]
    print('Track task %s progress' % file_name)
    with open(file_path, 'r') as log_file:
        # log_file.seek(0,2)
        wait_cont = 0
        simulation_state = False
        while True:
            line = log_file.readline()
            if not line:
                time.sleep(1)
                wait_cont += 1
                continue

            if 'TIMING:' in line:
                remaing_time = [item for item in line.split(' ') if item][8]
                if float(remaing_time) <= 1:
                    remaing_time == str(remaing_time * 60) + 'min'
                else:
                    remaing_time == str(remaing_time) + 'hours'

            elif 'PERFORMANCE:' in line:
                averag_performance = [item for item in line.split(' ') if item][3]
                sys.stdout.write('\r')
                print('%s : job: %s , remain_time: %s , performance: %s ns/day              ' %(get_time(),file_name ,remaing_time, averag_performance), end='',flush=True)
                wait_cont = 0

            elif 'TCL: Running for' in line:
                simulation_state = True

            elif'ERROR: Constraint failure in RATTLE algorithm' in line: #增加能量最小化
                print('processing error !!!!!')

            elif 'CPUTime' in line:
                print('\n job %s has finished!'%file_name)
                update_center()
                break


            if simulation_state == True and wait_cont >= 20:  #删除norepeat参数
                print('simulation faild')


if __name__ == '__main__':
    current_path = os.getcwd()
    folder_list = get_folder_list(current_path)
    for folder in folder_list[4:]:
        confige_list = get_config_list(folder)
        for config_file in confige_list:
            confige_file_path = os.path.join(folder,config_file)
            log_file_path = confige_file_path[:-len('.conf')]+'.log'
            command = 'namd3 +p8 +idlepoll +devices 0 %s > %s &'%(confige_file_path, log_file_path)
            print('process command: %s' % command)
            os.system(command)
            read_log(log_file_path, confige_file_path, command)

