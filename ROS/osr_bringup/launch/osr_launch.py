import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    config_dir = os.path.join(
        get_package_share_directory('osr_bringup'),
        'config'
    )
    
    roboclaw_params = os.path.join(config_dir, 'roboclaw_params.yaml')
    roboclaw_mod_params = os.path.join(config_dir, 'roboclaw_params_mod.yaml')
    osr_params = os.path.join(config_dir, 'osr_params.yaml')
    osr_mod_params = os.path.join(config_dir, 'osr_params_mod.yaml')
    servo_params = os.path.join(config_dir, 'servo_params.yaml')
    servo_mod_params = os.path.join(config_dir, 'servo_params_mod.yaml')
    joystick_params = os.path.join(config_dir, 'joystick_params.yaml')
    joystick_mod_params = os.path.join(config_dir, 'joystick_params_mod.yaml')

    # Build parameter lists - include mod files if they exist
    roboclaw_param_list = [roboclaw_params]
    if os.path.exists(roboclaw_mod_params):
        roboclaw_param_list.append(roboclaw_mod_params)

    osr_param_list = [osr_params]
    if os.path.exists(osr_mod_params):
        osr_param_list.append(osr_mod_params)

    servo_param_list = [servo_params]
    if os.path.exists(servo_mod_params):
        servo_param_list.append(servo_mod_params)
    
    joystick_param_list = [joystick_params]
    if os.path.exists(joystick_mod_params):
        joystick_param_list.append(joystick_mod_params)

    ld = LaunchDescription()
    
    ld.add_action(
        Node(
            package='osr_control',
            executable='roboclaw_wrapper',
            name='roboclaw_wrapper',
            output='screen',
            emulate_tty=True,
            respawn=True,
            parameters=roboclaw_param_list
        )
    )
    ld.add_action(
        Node(
            package='osr_control',
            executable='servo_control',
            name='servo_wrapper',
            output='screen',
            emulate_tty=True,
            respawn=True,
            parameters=servo_param_list  # mod_params override base params if file exists
        )
    )
    ld.add_action(
        DeclareLaunchArgument('enable_odometry', default_value='false')
    )
    ld.add_action(
        DeclareLaunchArgument('publish_transform', default_value='false')
    )
    ld.add_action(
        Node(
            package='osr_control',
            executable='rover',
            name='rover',
            output='screen',
            emulate_tty=True,
            respawn=True,
            parameters=osr_param_list + [
                        {'enable_odometry': LaunchConfiguration('enable_odometry'),
                         'publish_transform': LaunchConfiguration('publish_transform')}]
        )
    )
    ld.add_action(
        Node(
            package='teleop_twist_joy',
            executable='teleop_node',
            name='teleop_twist_joy',
            output='screen',
            emulate_tty=True,
            respawn=True,
            parameters=joystick_param_list,  # mod_params override base params if file exists
            remappings=[
                ('/cmd_vel', '/cmd_vel_intuitive')
            ]
        )
    )
    ld.add_action(
        Node(
            package='joy',
            executable='joy_node',
            name='joy',
            output='screen',
            emulate_tty=True,
            respawn=True,
            parameters=[
                {"autorepeat_rate": 5.0},
                {"device_id": 0},  # This might be different on your computer. Run `ls -l /dev/input/event*`. If you have event1, put 1.
            ]        
        )
    )
    ld.add_action(
        Node(
            package='osr_control',
            executable='ina260',
            name='ina260_node',
            output='screen',
            emulate_tty=True,
            parameters=[
                {"publish_rate": 1.0},
                {"sensor_address": "0x45"},
            ]        
        )
    )
    # ld.add_action(
    #     Node(
    #         package='osr_control',
    #         executable='joy_extras',
    #         output='screen',
    #         emulate_tty=True,
    #         parameters=[
    #             {"duty_button_index": 1}  # which button toggles duty mode on/off
    #         ]
    #     )
    # )

    return ld
