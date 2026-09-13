import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from sensor_msgs.msg import Temperature
from std_msgs.msg import Float32, String
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose


class MissionController(Node):

    def __init__(self):
        super().__init__('mission_controller')

        # -------------------------------
        # Sensor values
        # -------------------------------

        self.temperature = None
        self.pressure = None
        self.gas_level = None

        self.create_subscription(
            Temperature,
            '/temperature',
            self.temperature_callback,
            10
        )

        self.create_subscription(
            Float32,
            '/pressure',
            self.pressure_callback,
            10
        )

        self.create_subscription(
            Float32,
            '/gas_level',
            self.gas_callback,
            10
        )

        # -------------------------------
        # Inspection report
        # -------------------------------

        self.report_pub = self.create_publisher(
            String,
            '/inspection_report',
            10
        )

        # -------------------------------
        # Nav2 Action Client
        # -------------------------------

        self.nav_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

        # -------------------------------
        # Inspection points
        # -------------------------------

        self.points = [
            ('IP1', -5.0, 0.5),
            ('IP2', 2.0, 0.5),
            ('IP3', 5.0, -1.5)
        ]

        self.home = ('HOME', 5.8, -4.2)

        self.current_point = 0
        self.goal_handle = None
        self.inspect_timer = None
        self.mission_started = False

        # -------------------------------
        # Mission start timer
        # -------------------------------

        self.start_timer = self.create_timer(
            5.0,
            self.start_mission
        )

        self.get_logger().info('====================================')
        self.get_logger().info(' Hazardous Inspection Robot')
        self.get_logger().info(' Mission Controller Started')
        self.get_logger().info(' State: IDLE')
        self.get_logger().info('====================================')

    # ==================================================
    # SENSOR CALLBACKS
    # ==================================================

    def temperature_callback(self, msg):
        self.temperature = msg.temperature

    def pressure_callback(self, msg):
        self.pressure = msg.data

    def gas_callback(self, msg):
        self.gas_level = msg.data

    # ==================================================
    # START MISSION
    # ==================================================

    def start_mission(self):

        if self.mission_started:
            return

        self.mission_started = True
        self.start_timer.cancel()

        self.get_logger().info(
            'Starting autonomous inspection mission.'
        )

        self.current_point = 0
        self.go_to_next_point()

    # ==================================================
    # NAVIGATE TO NEXT INSPECTION POINT
    # ==================================================

    def go_to_next_point(self):

        if self.current_point >= len(self.points):
            self.return_home()
            return

        name, x, y = self.points[self.current_point]

        self.get_logger().info(
            f'Navigating to {name}...'
        )

        self.send_goal(x, y, name)

    # ==================================================
    # SEND NAV2 GOAL
    # ==================================================

    def send_goal(self, x, y, location_name):

        if not self.nav_client.wait_for_server(timeout_sec=5.0):

            self.get_logger().error(
                'Nav2 action server is not available.'
            )

            return

        goal_msg = NavigateToPose.Goal()

        goal_msg.pose = PoseStamped()

        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = (
            self.get_clock().now().to_msg()
        )

        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.position.z = 0.0

        goal_msg.pose.pose.orientation.x = 0.0
        goal_msg.pose.pose.orientation.y = 0.0
        goal_msg.pose.pose.orientation.z = 0.0
        goal_msg.pose.pose.orientation.w = 1.0

        future = self.nav_client.send_goal_async(
            goal_msg
        )

        future.add_done_callback(
            lambda future: self.goal_response_callback(
                future,
                location_name
            )
        )

    # ==================================================
    # NAV2 GOAL RESPONSE
    # ==================================================

    def goal_response_callback(
        self,
        future,
        location_name
    ):

        self.goal_handle = future.result()

        if not self.goal_handle.accepted:

            self.get_logger().error(
                f'Navigation goal rejected: {location_name}'
            )

            return

        self.get_logger().info(
            f'Navigation goal accepted: {location_name}'
        )

        result_future = (
            self.goal_handle.get_result_async()
        )

        result_future.add_done_callback(
            lambda future: self.navigation_result_callback(
                future,
                location_name
            )
        )

    # ==================================================
    # NAVIGATION RESULT
    # ==================================================

    def navigation_result_callback(
        self,
        future,
        location_name
    ):

        result = future.result()

        # Nav2 status 4 = SUCCEEDED
        if result.status == 4:

            self.get_logger().info(
                f'Reached {location_name}.'
            )

            if location_name == 'HOME':

                self.get_logger().info(
                    '===================================='
                )

                self.get_logger().info(
                    ' INSPECTION MISSION COMPLETED'
                )

                self.get_logger().info(
                    ' Robot safely returned to HOME.'
                )

                self.get_logger().info(
                    '===================================='
                )

                return

            self.inspect_location()

        else:

            self.get_logger().error(
                f'Navigation failed at {location_name}.'
            )

    # ==================================================
    # INSPECTION
    # ==================================================

    def inspect_location(self):

        self.get_logger().info(
            '------------------------------------'
        )

        self.get_logger().info(
            'Inspecting environment...'
        )

        self.get_logger().info(
            'Reading temperature, pressure and gas sensors.'
        )

        # Wait 2 seconds before evaluating sensors
        if self.inspect_timer is not None:
            self.inspect_timer.cancel()

        self.inspect_timer = self.create_timer(
            2.0,
            self.evaluate_hazard
        )

    # ==================================================
    # HAZARD EVALUATION
    # ==================================================

    def evaluate_hazard(self):

        if (
            self.temperature is None
            or self.pressure is None
            or self.gas_level is None
        ):

            self.get_logger().warning(
                'Waiting for sensor readings...'
            )

            return

        # Stop inspection timer
        self.inspect_timer.cancel()
        self.inspect_timer = None

        location_name = self.points[
            self.current_point
        ][0]

        temperature = self.temperature
        pressure = self.pressure
        gas = self.gas_level

        # -------------------------------
        # Hazard classification
        # -------------------------------

        if (
            temperature >= 90.0
            or pressure >= 240.0
            or gas >= 70.0
        ):

            status = 'CRITICAL'

        elif (
            temperature >= 60.0
            or pressure >= 200.0
            or gas >= 20.0
        ):

            status = 'WARNING'

        else:

            status = 'SAFE'

        # -------------------------------
        # Create inspection report
        # -------------------------------

        report = (
            f'{location_name} | '
            f'Temperature: {temperature:.1f} C | '
            f'Pressure: {pressure:.1f} kPa | '
            f'Gas: {gas:.1f} ppm | '
            f'Status: {status}'
        )

        self.get_logger().info(
            '===================================='
        )

        self.get_logger().info(
            report
        )

        self.get_logger().info(
            '===================================='
        )

        # Publish report
        msg = String()
        msg.data = report

        self.report_pub.publish(msg)

        # -------------------------------
        # Critical hazard
        # -------------------------------

        if status == 'CRITICAL':

            self.get_logger().error(
                '!!! CRITICAL HAZARD DETECTED !!!'
            )

            self.get_logger().error(
                'Emergency return to HOME initiated.'
            )

            self.return_home()

            return

        # -------------------------------
        # Continue inspection
        # -------------------------------

        self.current_point += 1

        self.go_to_next_point()

    # ==================================================
    # RETURN HOME
    # ==================================================

    def return_home(self):

        name, x, y = self.home

        self.get_logger().warn(
            'Returning robot to safe HOME position.'
        )

        self.send_goal(
            x,
            y,
            name
        )


# ======================================================
# MAIN
# ======================================================

def main(args=None):

    rclpy.init(args=args)

    node = MissionController()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
