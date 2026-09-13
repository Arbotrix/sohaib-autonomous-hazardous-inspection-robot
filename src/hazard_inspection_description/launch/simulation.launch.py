import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    description_pkg = get_package_share_directory(
        'hazard_inspection_description'
    )

    gazebo_pkg = get_package_share_directory(
        'gazebo_ros'
    )

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

        # Gazebo + hazardous facility
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

        # Spawn inspection robot
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                spawn_robot_launch
            )
        )

    ])
