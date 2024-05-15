import pickle
import traci
import os
import time
import sys
from sumolib import checkBinary
import scipy.io

def generate_file_names(mat_file_path):
    # 提取文件名和扩展名
    base_name = mat_file_path.split('.')[0]
    extension = mat_file_path.split('.')[1]
    
    # 生成 mat_output_path
    mat_output_path = f"{base_name}_xy.{extension}"
    
    # 生成 file_name，按新规则在 base_name 后添加 to_all_vehicle_data
    file_name = f"{base_name}_to_all_vehicle_data.{extension}"
    
    return mat_output_path, file_name


if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'],'tools')
    sys.path.append(tools)
else:
    sys.exit("请声明环境变量 'SUMO_HOME'")


# .mat文件路径
mat_file_path = 'gatewayList1.mat'
# mat_output_path保存笛卡尔坐标到.mat文件, file_name存储仿真文件
mat_output_path, file_name = generate_file_names(mat_file_path)

# 加载.mat文件
mat_contents = scipy.io.loadmat(mat_file_path)
nodes_lat_lon = mat_contents['gatewayList']  # mat中对应的矩阵变量名


show_gui = True
sumoconfig_path = 'example.sumocfg'

if not show_gui:
    sumoBinary = checkBinary('sumo')
else:
    sumoBinary = checkBinary('sumo-gui')

# 加载 Sumo GUI 配置文件的路径, 已在sumoconfig中加载
# gui_settings_file = r'C:\Users\drzha\Desktop\self_sumo\test_view.xml'

# traci.start([sumoBinary,'-c',sumoconfig_path])
# traci.start([sumoBinary, '-c', sumoconfig_path, '--additional-files', 'gatewayList4_1.add.xml', '--gui-settings-file', gui_settings_file])

traci.start([sumoBinary, '-c', sumoconfig_path, '--gui-settings-file', 'vehicle_52.xml'])

# 转换经纬度为笛卡尔坐标，并同时保存原始的经纬度坐标以便对比,注意经纬度顺序
nodes_cartesian_and_geo = [(lon, lat, traci.simulation.convertGeo(lon, lat, fromGeo=True)) for lon, lat in nodes_lat_lon]

# 打印原始的经纬度坐标和转换后的笛卡尔坐标进行对比
# for i, (lat, lon, cartesian) in enumerate(nodes_cartesian_and_geo):
    # print(f"节点 {i}: 经纬度 = ({lat}, {lon}) -> 笛卡尔坐标 = {cartesian}")

# 从 nodes_cartesian_and_geo 中提取笛卡尔坐标
nodes_cartesian = [cartesian for _, _, cartesian in nodes_cartesian_and_geo]


scipy.io.savemat(mat_output_path, {'nodes_cartesian': nodes_cartesian})

all_vehicle_positions = []  # 保存每个步骤的 all_vehicle_position


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

# 将所有车辆数据保存到MAT文件中
scipy.io.savemat(file_name, {'all_vehicle_data': all_vehicle_data})

# 保存 all_vehicle_positions
# with open('all_vehicle_positions.pkl', 'wb') as f:

# with open('all_vehicle_positions_olmap.pkl', 'wb') as f:
#     pickle.dump(all_vehicle_positions, f)

