cd ~/arbotrix_capstone && cat > README.md <<'EOF'
# Autonomous Hazardous-Environment Inspection & Fault Reporting Robot

**Developed by:** Sohaib  
**Organization:** ARBotrix  
**Project Type:** Capstone Project 2026

## 1. Project Overview

An autonomous mobile robot designed to perform inspection missions inside simulated hazardous industrial environments where routine human inspection may be unsafe.

The robot autonomously navigates between predefined inspection points, collects simulated environmental and equipment-condition data, identifies abnormal conditions, reports inspection results, and safely returns to its charging/home station.

## 2. Problem Statement

Routine inspection of hazardous industrial areas can expose human workers to unsafe conditions such as excessive temperature, hazardous gas leakage, and abnormal equipment behavior.

The proposed system aims to reduce the need for human entry by using an autonomous mobile robot to perform routine inspection missions.

## 3. Proposed Solution

The robot operates in a simulated hazardous industrial facility using ROS 2, Gazebo, AMCL, and Nav2.

The robot:
- Starts from a designated charging/home station.
- Navigates autonomously to predefined inspection points.
- Simulates environmental and equipment sensors.
- Evaluates temperature, pressure, and gas-level readings.
- Classifies inspection conditions as SAFE, WARNING, or CRITICAL.
- Reports detected abnormalities.
- Returns to the charging/home station after completing the mission.

## 4. Core Technologies

- ROS 2 Humble
- Gazebo
- Nav2
- AMCL
- RViz2
- Python
- LiDAR-based navigation
- ROS 2 Services
- ROS 2 Action Clients
- State Machine
- Regulated Pure Pursuit (RPP)

## 5. Project Status

Day 1 — Project initialization and repository setup.  
Day 2 — Hazardous industrial facility and custom inspection robot development.  
Day 3 — Facility upgrades and autonomous navigation environment development.  
Day 4 — Robot motion and navigation configuration.  
Day 5 — Inspection sensors and mission controller integration.  
Final — Integrated autonomous inspection mission.

## 6. Installation & Setup

### Prerequisites

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo
- Python 3
- colcon
- RViz2

### Build

```bash
source /opt/ros/humble/setup.bash
cd ~/arbotrix_capstone
colcon build
source install/setup.bash

7. Running the Simulation
The system is launched using multiple terminals.
Terminal 1 — Gazebo
cd ~/arbotrix_capstone
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch hazard_inspection_description simulation.launch.py

Terminal 2 — Nav2
cd ~/arbotrix_capstone
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch hazard_inspection_robot nav2_bringup.launch.py

Terminal 3 — RViz2
cd ~/arbotrix_capstone
source /opt/ros/humble/setup.bash
source install/setup.bash
rviz2

Set the RViz Fixed Frame to:
map

Terminal 4 — Sensor Simulator
cd ~/arbotrix_capstone
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run hazard_inspection_robot sensor_simulator

Terminal 5 — Mission Controller
cd ~/arbotrix_capstone
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 run hazard_inspection_robot mission_controller

8. Autonomous Mission
The mission controller manages the inspection sequence:
HOME → IP1 → IP2 → IP3 → HOME

The robot uses Nav2 for autonomous navigation and predefined waypoints where required for safe obstacle clearance.
9. Inspection Data
The sensor simulator provides:
- Temperature
- Pressure
- Gas level
Example ROS 2 topics:
/temperature
/pressure
/gas_level

The mission controller evaluates the readings and classifies the inspection condition as:
SAFE
WARNING
CRITICAL

10. Navigation
The navigation system uses:
- LiDAR-based obstacle detection
- AMCL localization
- Nav2
- Global and local costmaps
- Inflation layers
- Regulated Pure Pursuit (RPP)
- Predefined navigation waypoints
Waypoints are used in constrained areas where direct navigation may bring the robot too close to obstacles.
11. Repository Structure
arbotrix_capstone/
├── src/
│   ├── hazard_inspection_description/
│   └── hazard_inspection_robot/
├── worlds/
├── README.md
└── ...

12. Mission Flow
1. Robot starts at HOME.
2. Robot navigates to IP1.
3. Robot performs inspection and receives simulated sensor values.
4. Robot navigates through safe waypoints toward IP2.
5. Robot performs the IP2 inspection.
6. Robot navigates toward IP3.
7. Robot performs the IP3 inspection.
8. Robot returns to HOME.
9. Inspection data and hazard status are reported through the mission controller.
   EOF
   git add README.md && git commit -m "Add project setup and execution instructions" && git push origin main
