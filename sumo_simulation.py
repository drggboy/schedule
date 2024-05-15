# sumo_simulation.py
import os
import sys
import traci
from sumolib import checkBinary
import scipy.io

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("请声明环境变量 'SUMO_HOME'")

def generate_file_names(mat_file_path):
    # 提取文件名和扩展名
    base_name = os.path.splitext(mat_file_path)[0]
    extension = os.path.splitext(mat_file_path)[1]
    
  
    # 生成 file_name，按新规则在 base_name 后添加 _to_all_vehicle_data
    file_name = f"{base_name}_to_all_vehicle_data{extension}"
    
    return file_name

show_gui = True
sumoconfig_path = 'example.sumocfg'

if not show_gui:
    sumoBinary = checkBinary('sumo')
else:
    sumoBinary = checkBinary('sumo-gui')

gui_settings_file = 'vehicle_52.xml'

# 启动 SUMO
traci.start([sumoBinary, '-c', sumoconfig_path, '--gui-settings-file', gui_settings_file])

# 使用 generate_file_names 来生成文件名
mat_file_path = 'gatewayList2.mat'  # 假设的输入文件
file_name = generate_file_names(mat_file_path)

all_vehicle_data = []
for step in range(0, 3600):
    traci.simulationStep(step + 1)
    
    # 初始化当前时间步的车辆数据列表
    step_vehicle_data = []
    
    for vehicle_id in traci.vehicle.getIDList():
        vehicle_data = {
            'id': vehicle_id,
            'position': traci.vehicle.getPosition(vehicle_id),
            'route': traci.vehicle.getRoute(vehicle_id),
        }
        
        # 将当前车辆的数据添加到当前时间步的列表中
        step_vehicle_data.append(vehicle_data)
        
        # 如果需要打印当前车辆信息，取消注释下面的行
        # print(f"Step {step + 1}: {vehicle_data}")

    # 将当前时间步的所有车辆数据作为一个单位添加到总数据列表中
    all_vehicle_data.append(step_vehicle_data)

traci.close()

# 保存车辆数据到.mat文件
scipy.io.savemat(file_name, {'all_vehicle_data': all_vehicle_data})
