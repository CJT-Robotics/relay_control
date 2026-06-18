# relay_control
# Relay Control Node

## Overview

The **Relay Control** is a ROS1 Noetic package designed to control a single-channel USB relay module (based on the CH340 USB-to-Serial converter chip) within a ROS environment.

It automatically detects the hardware device connected to you pc via its Vendor and Product IDs, tracks the relay state, and accepts state-change commands over a ROS topic. To protect the mechanical relay hardware from rapid, accidental triggering, the node features an internal, non-blocking software cooldown mechanism.

**Works perfectly with our [relay control plugin package](https://github.com/CJT-Robotics/relay_control_plugin.git)**

## Requirements

The node relies on the `pyserial` library to interface with the CH340 hardware chip.

Install it on your system:

```bash
pip3 install pyserial
```
## USB Permissions (Crucial)

By default, Ubuntu/Debian restricts access to serial interfaces. To allow your user to communicate with the relay without requiring `sudo` privileges, add your user to the `dialout` group:

```bash
sudo usermod -aG dialout $USER
```

> **Note:** You must log out and log back in (or reboot the system) for these group changes to take effect.

## Installation

Clone the repository into your Catkin workspace on the robot:

```bash
cd ~/catkin_ws/src
git clone git@github.com:CJT-Robotics/relay_control.git
```

Build the workspace:

```bash
cd ~/catkin_ws
catkin_make
```

Source your workspace and make the Python node executable:

```bash
sudo chmod +x src/relay_control/scripts/relay_node.py
source devel/setup.bash
```

## Usage

Start your `roscore` and launch the relay controller node directly:

```bash
rosrun relay_control relay_node.py
```

Upon a successful launch, the terminal will log the automatically detected serial port

### Turn the Relay ON

```bash
rostopic pub -1 cam_mount/relay_cmd std_msgs/String "data: 'on'"
```

### Turn the Relay OFF

```bash
rostopic pub -1 cam_mount/relay_cmd std_msgs/String "data: 'off'"
```

### Toggle the Relay State

```bash
rostopic pub -1 cam_mount/relay_cmd std_msgs/String "data: 'toggle'"
```

## Configuration

### Parameters & Constants

The following default hardware parameters and safety constraints are currently hardcoded in `relay_node.py` and can be adjusted if necessary.

| Setting             | Default Value       | Description                                                 |
| ------------------- | ------------------- | ----------------------------------------------------------- |
| `ch340_vid`         | `0x1A86`            | Vendor ID |
| `ch340_pid`         | `0x7523`            | Product ID     |
| `baud_rate`         | `9600`              | Baud rate          |
| `cooldown_duration` | `rospy.Duration(3)` | Minimum time buffer between consecutive relay state changes |

## Subscribed Topics

### `/cam_mount/relay_cmd`

**Type:**

```text
std_msgs/String
```

**Accepted Payloads:**

| Command    | Description                                                   |
| ---------- | ------------------------------------------------------------- |
| `"on"`     | Closes the relay circuit and turns the connected component ON |
| `"off"`    | Opens the relay circuit and turns the connected component OFF |
| `"toggle"` | Inverts the current relay state                               |

---

## Troubleshooting

## Fail-Safe Behavior

When the ROS node is terminated or shut down gracefully, the internal `shutdown_hook()` automatically sends the following safety packet:

```python
b'\xA0\x01\x00\xA1'
```

This forces the relay into the **OFF** state before releasing the serial port interface, helping prevent unintended hardware activation after node shutdown.