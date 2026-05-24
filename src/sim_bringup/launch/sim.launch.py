import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    SetEnvironmentVariable,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

# Gazebo converts package:// URIs to model:// and resolves them against
# GZ_SIM_RESOURCE_PATH. Adding the ROS2 share directories lets Gazebo find
# meshes installed under <pkg>/share/<pkg>/meshes/.
_ament_prefix = os.environ.get('AMENT_PREFIX_PATH', '')
_share_dirs = [os.path.join(p, 'share') for p in _ament_prefix.split(':') if p]
_gz_resource_path = ':'.join(
    filter(None, _share_dirs + [os.environ.get('GZ_SIM_RESOURCE_PATH', '')])
)


def launch_setup(context):
    robot = LaunchConfiguration('robot').perform(context)
    world = LaunchConfiguration('world').perform(context)
    x = LaunchConfiguration('x').perform(context)
    y = LaunchConfiguration('y').perform(context)
    yaw = LaunchConfiguration('yaw').perform(context)

    sim_bringup_share = get_package_share_directory('sim_bringup')

    world_file = os.path.join(sim_bringup_share, 'worlds', world, f'{world}.sdf')
    bridge_config = os.path.join(sim_bringup_share, 'config', 'bridges', f'{robot}.yaml')

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('ros_gz_sim'),
                'launch', 'gz_sim.launch.py'
            )
        ),
        launch_arguments={'gz_args': f'{world_file} -r'}.items(),
    )

    spawn = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(sim_bringup_share, 'launch', 'spawn_robot.launch.py')
        ),
        launch_arguments={
            'robot': robot,
            'x': x,
            'y': y,
            'yaw': yaw,
        }.items(),
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='gz_bridge',
        output='screen',
        parameters=[{'config_file': bridge_config}],
    )

    # Controller spawners run after Gazebo + gz_ros2_control are up
    joint_state_broadcaster = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )

    diff_drive_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_drive_controller', '--ros-args', '--remap',
                   '/diff_drive_controller/cmd_vel:=/cmd_vel'],
        output='screen',
    )

    delayed_controllers = TimerAction(
        period=5.0,
        actions=[joint_state_broadcaster, diff_drive_controller],
    )

    return [gz_sim, spawn, bridge, delayed_controllers]


def generate_launch_description():
    return LaunchDescription([
        SetEnvironmentVariable('GZ_SIM_RESOURCE_PATH', _gz_resource_path),
        DeclareLaunchArgument('robot', default_value='my_amr',
                              description='Robot name — must match a <robot>_sim package'),
        DeclareLaunchArgument('world', default_value='warehouse',
                              description='World name — must match worlds/<world>/<world>.sdf'),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
        OpaqueFunction(function=launch_setup),
    ])
