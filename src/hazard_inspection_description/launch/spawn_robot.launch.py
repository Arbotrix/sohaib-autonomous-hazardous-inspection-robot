import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'hazard_inspection_description'

    xacro_file = os.path.join(
        get_package_share_directory(package_name),
        'urdf',
        'inspection_robot.urdf.xacro'
    )

    robot_description = Command([
        'xacro ',
        xacro_file
    ])

    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    z_pose = LaunchConfiguration('z_pose')

    return LaunchDescription([

        DeclareLaunchArgument(
            'x_pose',
            default_value='5.8'
        ),

        DeclareLaunchArgument(
            'y_pose',
            default_value='-4.2'
        ),

        DeclareLaunchArgument(
            'z_pose',
            default_value='0.3'
        ),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[
                {
                    'robot_description': robot_description
                }
            ]
        ),

        Node(
            package='gazebo_ros',
            executable='spawn_entity.py',
            arguments=[
                '-topic',
                'robot_description',
                '-entity',
                'inspection_robot',
                '-x',
                x_pose,
                '-y',
                y_pose,
                '-z',
                z_pose
            ],
            output='screen'
        )

    ])
