import scipy.io
import os
import sys
from sumolib import checkBinary  # SUMO utility
import traci

# 假设SUMO环境变量已设置，否则需要在此处设置
if "SUMO_HOME" not in os.environ:
    sys.exit("请声明环境变量 'SUMO_HOME' 或在脚本中设置")

tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
sys.path.append(tools)
sumoconfig_path = 'example.sumocfg'
sumoBinary='sumo'
# 启动一个SUMO会话来进行地理坐标到笛卡尔坐标的转换
traci.start([checkBinary(sumoBinary), '-c',sumoconfig_path])  # 使用无GUI版本的SUMO

def convert_geo_to_cartesian(mat_file_path, mat_output_path):
    # 加载.mat文件
    mat_contents = scipy.io.loadmat(mat_file_path)
    nodes_lat_lon = mat_contents['gatewayList']  # mat中对应的矩阵变量名

    nodes_cartesian_and_geo = []
    for lon, lat in nodes_lat_lon:
        cartesian = traci.simulation.convertGeo(lon, lat, fromGeo=True)
        nodes_cartesian_and_geo.append((lon, lat, cartesian))
        print(f"转换：经纬度 = ({lat}, {lon}) -> 笛卡尔坐标 = {cartesian}")

    traci.close(False)  # 关闭SUMO会话

    nodes_cartesian = [cartesian for _, _, cartesian in nodes_cartesian_and_geo]
    scipy.io.savemat(mat_output_path, {'nodes_cartesian': nodes_cartesian})

def main():
    mat_file_path = 'gatewayList2.mat'  # 输入文件路径
    mat_output_path = 'gatewayList2_xy.mat'  # 输出文件路径

    convert_geo_to_cartesian(mat_file_path, mat_output_path)

if __name__ == "__main__":
    main()