import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    description_pkg = get_package_share_directory(
        'hazard_inspection_description'
    )

    gazebo_pkg = get_package_share_directory('gazebo_ros')

    world_file = os.path.join(
        os.path.expanduser('~/arbotrix_capstone'),
        'worlds',
        'hazardous_facility.world'
    )

    spawn_robot_launch = os.path.join(
        description_pkg,
        'launch',
        'spawn_robot.launch.py'
    )

    return LaunchDescription([

        # Start Gazebo with ROS interfaces
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    gazebo_pkg,
                    'launch',
                    'gazebo.launch.py'
                )
            ),
            launch_arguments={
                'world': world_file
            }.items()
        ),

        # Spawn our custom inspection robot
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                spawn_robot_launch
            )
        ),

        # Start SLAM Toolbox
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            name='slam_toolbox',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'base_frame': 'base_link',
                'odom_frame': 'odom',
                'map_frame': 'map',
                'scan_topic': '/scan',
                'mode': 'mapping',
                'resolution': 0.05,
                'max_laser_range': 10.0
            }]
        )

    ])
