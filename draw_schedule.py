import traci
import os
import time
import sys
from sumolib import checkBinary
import numpy as np
import scipy.io

def find_closest_rsu(vehicle_position, rsu_positions):
    # Calculate the Euclidean distance between the vehicle and each RSU
    distances = [np.linalg.norm(np.array(vehicle_position) - np.array(rsu_pos)) for rsu_pos in rsu_positions]
    # Return the closest RSU position
    closest_index = np.argmin(distances)
    return rsu_positions[closest_index]

def schedule_rsu(step, vehicle_i, nodes_cartesian, scheduling_results):  
    # Extract scheduling result for the current step and vehicle index
    current_step_schedule = scheduling_results[step][0][0]  # Access the cell for the current step
    vehicle_schedule = current_step_schedule[vehicle_i]  # Access the scheduling vector for the specific vehicle
    scheduled_positions = nodes_cartesian[vehicle_schedule-1]
    
    return scheduled_positions

    
def load_sumo_config(additional_files):
    if "SUMO_HOME" in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'],'tools')
        sys.path.append(tools)
    else:
        sys.exit("Please declare the environment variable 'SUMO_HOME'")

    show_gui = True
    sumoconfig_path = r'example.sumocfg'

    if not show_gui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # Load Sumo GUI configuration file path
    gui_settings_file = r'vehicle_52.xml'

    traci.start([sumoBinary, '-c', sumoconfig_path, '--additional-files', additional_files, '--gui-settings-file', gui_settings_file])


def convert_coordinates(nodes_lat_lon):
    # Convert latitude and longitude to Cartesian coordinates and save the original coordinates for comparison
    nodes_cartesian_and_geo = [(lon, lat, traci.simulation.convertGeo(lon, lat, fromGeo=True)) for lon, lat in nodes_lat_lon]

    # Print the original coordinates and the converted Cartesian coordinates for comparison
    for i, (lat, lon, cartesian) in enumerate(nodes_cartesian_and_geo):
        print(f"Node {i}: Latitude = ({lat}, {lon}) -> Cartesian coordinates = {cartesian}")

    # Extract Cartesian coordinates from nodes_cartesian_and_geo
    nodes_cartesian = [cartesian for _, _, cartesian in nodes_cartesian_and_geo]

    return nodes_cartesian

def create_vehicle_lines(nodes_cartesian, scheduling_results):
    previous_lines = {}  # Store the line IDs of each vehicle in the previous time step

    for step in range(0, 3600):
        traci.simulationStep()
        # time.sleep(3)

        # Remove all lines from the previous time step
        current_polygons = traci.polygon.getIDList()
        for vehicle_id, line_id in previous_lines.items():
            if line_id in current_polygons:
                traci.polygon.remove(line_id)

        # Update line storage
        previous_lines.clear()

        # Create new lines for each vehicle
        for vehicle_i, vehicle_id in enumerate(traci.vehicle.getIDList()):
            vehicle_position = traci.vehicle.getPosition(vehicle_id)
            # closest_rsu_position = find_closest_rsu(vehicle_position, nodes_cartesian)
            schedule_rsu_position = schedule_rsu(step, vehicle_i, nodes_cartesian, scheduling_results)
            # Generate a unique line ID
            line_id = f"{step}_{vehicle_id}_to_rsu"
            previous_lines[vehicle_id] = line_id

            # Use polygon to add a new line, but only use two very close points to create a thin line
            traci.polygon.add(line_id, [vehicle_position, schedule_rsu_position], color=(255, 0, 0, 255), layer=100, fill=False, lineWidth=0.1)
        print(step)
    traci.close()

# Main function
def main():
    # 调度结果 .mat 文件路径
    schedule_mat_file_path = 'ACO_S.mat'
    schedule_mat_contents = scipy.io.loadmat(schedule_mat_file_path)
    scheduling_results = schedule_mat_contents['ACO_S']  # Variable name in the mat file

    # 中继节点经纬度位置 .mat 文件路径
    relay_mat_file_path = 'gatewayList1.mat'
    relay_mat_contents = scipy.io.loadmat(relay_mat_file_path)
    nodes_lat_lon = relay_mat_contents['gatewayList']  # Variable name in the mat file

    # Additional files for SUMO
    additional_files = 'gatewayList1.add.xml'

    load_sumo_config(additional_files)
    nodes_cartesian = convert_coordinates(nodes_lat_lon)
    create_vehicle_lines(nodes_cartesian, scheduling_results)

if __name__ == "__main__":
    main()

