import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Temperature
from std_msgs.msg import Float32
from geometry_msgs.msg import PoseWithCovarianceStamped


class SensorSimulator(Node):

    def __init__(self):
        super().__init__('sensor_simulator')

        self.temperature_pub = self.create_publisher(
            Temperature, '/temperature', 10)

        self.pressure_pub = self.create_publisher(
            Float32, '/pressure', 10)

        self.gas_pub = self.create_publisher(
            Float32, '/gas_level', 10)

        self.pose_sub = self.create_subscription(
            PoseWithCovarianceStamped,
            '/amcl_pose',
            self.pose_callback,
            10)

        self.x = 5.8
        self.y = -4.2

        self.timer = self.create_timer(
            1.0, self.publish_sensor_data)

        self.get_logger().info('====================================')
        self.get_logger().info(' Hazard Sensor Simulator Started')
        self.get_logger().info(' Temperature: /temperature')
        self.get_logger().info(' Pressure:    /pressure')
        self.get_logger().info(' Gas:         /gas_level')
        self.get_logger().info('====================================')

    def pose_callback(self, msg):

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

    def get_sensor_values(self):

        # IP1
        if math.hypot(self.x - (-5.0), self.y - 0.5) < 1.0:
            return 40.0, 180.0, 5.0, 'IP1'

        # IP2
        elif math.hypot(self.x - 2.0, self.y - 0.5) < 1.0:
            return 65.0, 210.0, 25.0, 'IP2'

        # IP3
        elif math.hypot(self.x - 5.0, self.y - (-1.5)) < 1.0:
            return 95.0, 250.0, 80.0, 'IP3'

        # Normal environment
        return 25.0, 101.0, 0.0, 'NORMAL'

    def publish_sensor_data(self):

        temperature_value, pressure_value, gas_value, location = \
            self.get_sensor_values()

        temperature = Temperature()
        temperature.header.stamp = self.get_clock().now().to_msg()
        temperature.header.frame_id = 'base_link'
        temperature.temperature = temperature_value
        temperature.variance = 0.0

        pressure = Float32()
        pressure.data = pressure_value

        gas = Float32()
        gas.data = gas_value

        self.temperature_pub.publish(temperature)
        self.pressure_pub.publish(pressure)
        self.gas_pub.publish(gas)

        self.get_logger().info(
            f'{location} | '
            f'Temp: {temperature_value:.1f} C | '
            f'Pressure: {pressure_value:.1f} kPa | '
            f'Gas: {gas_value:.1f} ppm'
        )


def main(args=None):

    rclpy.init(args=args)

    node = SensorSimulator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
