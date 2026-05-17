# simulation_ws

Gazebo simulation workspace for AMR development. Contains world environments, robot simulation descriptions, and launch orchestration. Robot source code lives separately in `my_amr/`.

## Prerequisites

### ROS2 Jazzy

Follow the [official installation guide](https://docs.ros.org/en/jazzy/Installation.html) for your platform. The `ros-jazzy-desktop` variant is recommended (includes RViz and rqt).

### Gazebo Harmonic

Jazzy's default simulator is Gazebo Harmonic. Install the full ROS–Gazebo integration meta-package:

```bash
sudo apt install ros-jazzy-ros-gz
```

This pulls in `gz-harmonic`, `ros_gz_sim`, `ros_gz_bridge`, and `ros_gz_image`.

### This workspace's dependencies

```bash
sudo apt install \
  ros-jazzy-gz-ros2-control \
  ros-jazzy-controller-manager \
  ros-jazzy-diff-drive-controller \
  ros-jazzy-joint-state-broadcaster \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-xacro
```

## Structure

```
simulation_ws/
├── models/                        # Custom Gazebo models
└── src/
    ├── my_amr_sim/                # Sim description for my_amr robot
    │   ├── urdf/
    │   │   ├── my_amr.urdf.xacro  # Robot geometry + sensors + Gazebo plugins
    │   │   └── ros2_control.xacro # gz_ros2_control hardware interface
    │   ├── config/
    │   │   └── controllers.yaml   # diff_drive_controller + joint_state_broadcaster
    │   └── meshes/
    └── sim_bringup/               # Orchestration: worlds, launch, bridge configs
        ├── launch/
        │   ├── sim.launch.py      # Top-level entry point
        │   └── spawn_robot.launch.py
        ├── worlds/
        │   ├── warehouse/         # 20 × 20 m warehouse with shelf rows
        │   └── hospital/          # 30 × 20 m hospital with corridor
        └── config/
            └── bridges/
                └── my_amr.yaml   # ros_gz_bridge topic mappings
```

### Adding a new robot

1. Create `src/<robot_name>_sim/` mirroring `my_amr_sim/`
2. Add `src/sim_bringup/config/bridges/<robot_name>.yaml`
3. Declare the new package as an `exec_depend` in `sim_bringup/package.xml`

### Adding a new world

1. Create `src/sim_bringup/worlds/<world_name>/<world_name>.sdf`
2. `colcon build` — `setup.py` picks up new world directories automatically

## Build

```bash
cd ~/workspace/simulation_ws
colcon build
source install/setup.bash
```

## Usage

```bash
# Default: my_amr in the warehouse
ros2 launch sim_bringup sim.launch.py

# Choose robot and world
ros2 launch sim_bringup sim.launch.py robot:=my_amr world:=hospital

# Spawn at a specific pose
ros2 launch sim_bringup sim.launch.py robot:=my_amr world:=warehouse x:=2.0 y:=-1.0 yaw:=1.57
```

## Topic reference

| Topic | Direction | Type |
|---|---|---|
| `/cmd_vel` | ROS → controller | `geometry_msgs/Twist` |
| `/odom` | controller → ROS | `nav_msgs/Odometry` |
| `/scan` | Gazebo → ROS (bridged) | `sensor_msgs/LaserScan` |
| `/clock` | Gazebo → ROS (bridged) | `rosgraph_msgs/Clock` |
| `/joint_states` | controller → ROS | `sensor_msgs/JointState` |
| `/tf` | robot_state_publisher | — |

`/cmd_vel` and `/odom` are handled natively by `gz_ros2_control` — no bridge entry needed.

## Sim time

All nodes launched here run with `use_sim_time: true`. Make sure any external node (e.g. Nav2) is also started with `use_sim_time:=true`.
