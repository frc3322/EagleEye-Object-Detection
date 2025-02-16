import numpy as np
array = np.array

class Constants:
    log = True
    print_terminal = True
    detection_logging = False

    simulation_mode = True

class NetworkTableConstants:
    server_address = '10.0.0.62'
    robot_position_key = 'robot_position'
    robot_rotation_key = 'robot_rotation'

class ObjectDetectionConstants:
    input_size = 320
    confidence_threshold = 0.35
    note_combined_threshold = .25

class DisplayConstants:
    run_web_server = True

class CameraConstants:
    camera_list = [{'name': 'front', 'camera_id': 0, 'fov': array([70, 38]), 'camera_offset_pos': array([ 0.25  ,  0.  , 0.75]), 'camera_pitch': 0, 'camera_yaw': 0}]
