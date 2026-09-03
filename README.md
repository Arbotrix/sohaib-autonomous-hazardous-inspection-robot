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

The robot will operate in a simulated hazardous industrial facility using ROS 2, Gazebo, AMCL, and Nav2.

The robot will:

- Start from a designated charging/home station.
- Navigate autonomously to predefined inspection points.
- Simulate environmental and equipment sensors.
- Evaluate temperature and gas-level readings.
- Classify inspection conditions as SAFE, WARNING, or CRITICAL.
- Report detected abnormalities.
- Return to the charging/home station after completing or safely terminating the mission.

## 4. Core Technologies

- ROS 2
- Gazebo
- Nav2
- AMCL
- RViz
- Python
- LiDAR-based navigation
- ROS 2 Services
- ROS 2 Action Clients
- State Machine

## 5. Project Status

Day 1 — Project initialization and repository setup.
