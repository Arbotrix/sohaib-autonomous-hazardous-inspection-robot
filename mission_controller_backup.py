import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient

from geometry_msgs.msg import PoseStamped
from std_msgs.msg import String, Float32
from sensor_msgs.msg import Temperature
from nav2_msgs.action import NavigateToPose


class MissionController(Node):

    def __init__(self):
        super().__init__('mission_controller')

        self.nav_client = ActionClient(
            self,
            NavigateToPose,
            '/navigate_to_pose'
        )

        self.report_pub = self.create_publisher(
            String,
            '/inspection_report',
            10
        )

        self.temperature = 25.0
        self.pressure = 101.0
        self.gas_level = 0.0

        self.create_subscription(
            Temperature, '/temperature',
            self.temperature_callback, 10
        )

        self.create_subscription(
            Float32, '/pressure',
            self.pressure_callback, 10
        )

        self.create_subscription(
            Float32, '/gas_level',
            self.gas_callback, 10
        )

        # Map-frame inspection points
        self.points = [
            ('IP1', -5.20, 0.19),
            ('IP2', 1.7557, 0.4057),
            ('IP3', 5.7298, -1.7980)
        ]

        # Confirmed Nav2 map-frame HOME
        self.home = ('HOME', 6.37, -5.11)

        self.current_point_index = 0
        self.route_queue = []
        self.current_target = None

        self.goal_handle = None
        self.goal_sent = False
        self.retry_count = 0
        self.max_retries = 3

        self.inspect_timer = None

        self.mission_started = False

        self.start_timer = self.create_timer(
            5.0,
            self.start_mission
        )

        self.get_logger().info(
            'Mission controller started.'
        )

    # =========================================================
    # SENSOR CALLBACKS
    # =========================================================

    def temperature_callback(self, msg):
        self.temperature = msg.temperature

    def pressure_callback(self, msg):
        self.pressure = msg.data

    def gas_callback(self, msg):
        self.gas_level = msg.data

    # =========================================================
    # START MISSION
    # =========================================================

    def start_mission(self):

        if self.mission_started:
            return

        self.mission_started = True
        self.start_timer.cancel()

        self.get_logger().info(
            'Starting autonomous inspection mission.'
        )

        self.current_point_index = 0
        self.go_to_next_point()

    # =========================================================
    # NAVIGATION
    # =========================================================

    def go_to_next_point(self):

        if self.current_point_index >= len(self.points):

            self.get_logger().info(
                'All inspection points completed.'
            )

            self.return_home()
            return

        point = self.points[self.current_point_index]

        if point[0] == 'IP1':
            self.route_queue = [point]
        else:
            self.route_queue = [point]

        self.current_target = point
        self.retry_count = 0

        self.get_logger().info(
            f'Navigating to {point[0]} '
            f'({point[1]:.2f}, {point[2]:.2f})'
        )

        self.send_next_route_goal()

    def send_next_route_goal(self):

        if not self.route_queue:
            self.start_inspection()
            return

        target = self.route_queue.pop(0)

        self.current_target = target
        self.goal_sent = False

        self.send_navigation_goal(
            target[0],
            target[1],
            target[2]
        )

    def send_navigation_goal(self, name, x, y):

        if self.goal_sent:
            return

        self.goal_sent = True

        if not self.nav_client.wait_for_server(timeout_sec=5.0):

            self.get_logger().error(
                'Nav2 action server unavailable.'
            )

            self.goal_sent = False
            self.retry_navigation()
            return

        goal_msg = NavigateToPose.Goal()

        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()

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
            self.goal_response_callback
        )

        self.get_logger().info(
            f'Navigation goal sent: {name}'
        )

    def goal_response_callback(self, future):

        self.goal_handle = future.result()

        if self.goal_handle is None or not self.goal_handle.accepted:

            self.get_logger().warn(
                'Navigation goal rejected.'
            )

            self.goal_sent = False
            self.retry_navigation()
            return

        self.get_logger().info(
            'Navigation goal accepted.'
        )

        result_future = self.goal_handle.get_result_async()

        result_future.add_done_callback(
            self.navigation_result_callback
        )

    def navigation_result_callback(self, future):

        self.goal_sent = False

        result = future.result()

        status = result.status

        if status == 4:

            self.retry_count = 0

            self.get_logger().info(
                f'Reached {self.current_target[0]}.'
            )

            if self.current_target[0].startswith('IP'):

                self.start_inspection()

            else:

                self.send_next_route_goal()

        else:

            self.get_logger().warn(
                f'Navigation failed at '
                f'{self.current_target[0]}. '
                f'Nav2 status: {status}'
            )

            self.retry_navigation()

    # =========================================================
    # RETRY / REPLAN
    # =========================================================

    def retry_navigation(self):

        if self.retry_count >= self.max_retries:

            self.get_logger().error(
                f'Navigation failed after '
                f'{self.max_retries} retries.'
            )

            self.goal_sent = False
            return

        self.retry_count += 1

        self.get_logger().warn(
            f'Retrying {self.current_target[0]} '
            f'({self.retry_count}/{self.max_retries})'
        )

        self.retry_timer = self.create_timer(
            2.0,
            self.retry_timer_callback
        )

    def retry_timer_callback(self):

        if hasattr(self, 'retry_timer'):
            self.retry_timer.cancel()

        self.goal_sent = False

        if self.current_target is None:
            return

        self.send_navigation_goal(
            self.current_target[0],
            self.current_target[1],
            self.current_target[2]
        )

    # =========================================================
    # INSPECTION
    # =========================================================

    def start_inspection(self):

        self.get_logger().info(
            f'Inspecting {self.current_target[0]}...'
        )

        if self.inspect_timer is not None:
            self.inspect_timer.cancel()

        self.inspect_timer = self.create_timer(
            3.0,
            self.perform_inspection
        )

    def perform_inspection(self):

        if self.inspect_timer is not None:
            self.inspect_timer.cancel()
            self.inspect_timer = None

        temperature = self.temperature
        pressure = self.pressure
        gas = self.gas_level

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

        report = (
            f'{self.current_target[0]} | '
            f'Status: {status} | '
            f'Temperature: {temperature:.1f} C | '
            f'Pressure: {pressure:.1f} kPa | '
            f'Gas: {gas:.1f} ppm'
        )

        self.get_logger().info(
            f'INSPECTION REPORT: {report}'
        )

        msg = String()
        msg.data = report

        self.report_pub.publish(msg)

        if status == 'CRITICAL':

            self.get_logger().error(
                'CRITICAL HAZARD DETECTED! '
                'Returning to HOME.'
            )

            self.return_home()
            return

        self.current_point_index += 1

        self.go_to_next_point()

    # =========================================================
    # RETURN HOME
    # =========================================================

    def return_home(self):

        self.current_target = self.home
        self.retry_count = 0
        self.route_queue = []

        self.get_logger().warn(
            'Returning to HOME.'
        )

        self.send_navigation_goal(
            self.home[0],
            self.home[1],
            self.home[2]
        )


def main(args=None):

    rclpy.init(args=args)

    node = MissionController()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
