import rclpy
from rclpy.node import Node
from enum import Enum


class MissionState(Enum):
    IDLE = 1
    NAVIGATING = 2
    INSPECTING = 3
    RETURNING = 4
    ERROR = 5


class MissionController(Node):

    def __init__(self):
        super().__init__('mission_controller')

        self.state = MissionState.IDLE

        self.get_logger().info('====================================')
        self.get_logger().info(' Hazardous Inspection Robot')
        self.get_logger().info(' Mission Controller Started')
        self.get_logger().info(' State: IDLE')
        self.get_logger().info('====================================')


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
