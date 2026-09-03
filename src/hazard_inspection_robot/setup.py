from setuptools import find_packages, setup

package_name = 'hazard_inspection_robot'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Sohaib',
    maintainer_email='shahamdan668@gmail.com',
    description='Autonomous hazardous-environment inspection and fault reporting robot',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'mission_controller = hazard_inspection_robot.mission_controller:main',
        ],
    },
)
