import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'hazard_inspection_robot'

    package_share = get_package_share_directory(package_name)

    nav2_params = os.path.join(
        package_share,
        'config',
        'nav2_params.yaml'
    )

    map_file = os.path.expanduser(
        '~/arbotrix_capstone/maps/hazardous_facility.yaml'
    )

    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true'
        ),

        # =========================
        # MAP SERVER
        # =========================

        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[
                nav2_params,
                {
                    'yaml_filename': map_file,
                    'use_sim_time': use_sim_time
                }
            ]
        ),

        # =========================
        # AMCL
        # =========================

        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[
                nav2_params,
                {
                    'use_sim_time': use_sim_time
                }
            ]
        ),

        # =========================
        # PLANNER SERVER
        # =========================

        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[
                nav2_params,
                {
                    'use_sim_time': use_sim_time
                }
            ]
        ),

        # =========================
        # CONTROLLER SERVER
        # =========================

        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            output='screen',
            parameters=[
                nav2_params,
                {
                    'use_sim_time': use_sim_time
                }
            ]
        ),

        # =========================
        # BEHAVIOR TREE NAVIGATOR
        # =========================

        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            name='bt_navigator',
            output='screen',
            parameters=[
                nav2_params,
                {
                    'use_sim_time': use_sim_time
                }
            ]
        ),

        # =========================
        # BEHAVIOR SERVER
        # =========================

        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            name='behavior_server',
            output='screen',
            parameters=[
                nav2_params,
                {
                    'use_sim_time': use_sim_time
                }
            ]
        ),

        # =========================
        # WAYPOINT FOLLOWER
        # =========================

        Node(
            package='nav2_waypoint_follower',
            executable='waypoint_follower',
            name='waypoint_follower',
            output='screen',
            parameters=[
                nav2_params,
                {
                    'use_sim_time': use_sim_time
                }
            ]
        ),

        # =========================
        # VELOCITY SMOOTHER
        # =========================

        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            name='velocity_smoother',
            output='screen',
            parameters=[
                nav2_params,
                {
                    'use_sim_time': use_sim_time
                }
            ]
        ),

        # =========================
        # LOCALIZATION LIFECYCLE
        # =========================

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_localization',
            output='screen',
            parameters=[
                {
                    'use_sim_time': use_sim_time,
                    'autostart': True,
                    'node_names': [
                        'map_server',
                        'amcl'
                    ]
                }
            ]
        ),

        # =========================
        # NAVIGATION LIFECYCLE
        # =========================

        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[
                {
                    'use_sim_time': use_sim_time,
                    'autostart': True,
                    'node_names': [
                        'planner_server',
                        'controller_server',
                        'bt_navigator',
                        'behavior_server',
                        'waypoint_follower',
                        'velocity_smoother'
                    ]
                }
            ]
        ),

    ])
