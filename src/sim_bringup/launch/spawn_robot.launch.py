import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def launch_setup(context):
    robot = LaunchConfiguration('robot').perform(context)
    x = LaunchConfiguration('x').perform(context)
    y = LaunchConfiguration('y').perform(context)
    yaw = LaunchConfiguration('yaw').perform(context)

    urdf_path = os.path.join(
        get_package_share_directory(f'{robot}_sim'),
        'urdf', f'{robot}.urdf.xacro'
    )
    robot_description = xacro.process_file(urdf_path).toxml()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': True,
        }],
    )

    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        output='screen',
        arguments=[
            '-name', robot,
            '-string', robot_description,
            '-x', x,
            '-y', y,
            '-z', '0.1',
            '-Y', yaw,
        ],
    )

    return [robot_state_publisher, spawn]


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('robot', default_value='my_amr'),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
        OpaqueFunction(function=launch_setup),
    ])
