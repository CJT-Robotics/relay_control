#!/usr/bin/env python3
import rospy
from std_msgs.msg import String
import serial
import serial.tools.list_ports
import sys

class RelayControlNode:
    def __init__(self):
        rospy.init_node('relay_control_node', anonymous=False)
        
        self.ch340_vid = 0x1A86
        self.ch340_pid = 0x7523
        self.baud_rate = 9600
        
        self.relay_on = b'\xA0\x01\x01\xA2'
        self.relay_off = b'\xA0\x01\x00\xA1'

        self.relay_state = False 
        
        self.cooldown_duration = rospy.Duration(3)
        self.last_switch_time = rospy.Time(0)
        
        self.serial_port = self.find_relay_port()
        if not self.serial_port:
            rospy.logerr("Relais not found")
            sys.exit(1)

        try:
            self.ser = serial.Serial(self.serial_port, self.baud_rate, timeout=1)
            self.set_relay(False)
            rospy.loginfo(f"Relais on port: {self.serial_port}")
        except serial.SerialException as e:
            rospy.logerr(e)
            sys.exit(1)
            
        self.sub = rospy.Subscriber('cam_mount/relay_cmd', String, self.command_callback)
        
        rospy.on_shutdown(self.shutdown_hook)

    def find_relay_port(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.vid == self.ch340_vid and port.pid == self.ch340_pid:
                return port.device
        return None

    def set_relay(self, state):
        if state:
            self.ser.write(self.relay_on)
            self.relay_state = True
        else:
            self.ser.write(self.relay_off)
            self.relay_state = False
        self.ser.flush()
        
        self.last_switch_time = rospy.Time.now()

    def command_callback(self, msg):
        cmd = msg.data.lower().strip()
        
        if cmd not in ["on", "off", "toggle"]:
            return

        current_time = rospy.Time.now()
        
        time_since_last_switch = current_time - self.last_switch_time
        if time_since_last_switch < self.cooldown_duration:
            return
        
        try:
            if cmd == "on":
                if not self.relay_state:
                    self.set_relay(True)
            elif cmd == "off":
                if self.relay_state:
                    self.set_relay(False)
            elif cmd == "toggle":
                self.set_relay(not self.relay_state)
        except serial.SerialException as e:
            rospy.logerr(e)

    def shutdown_hook(self):
        if hasattr(self, 'ser') and self.ser.is_open:
            self.ser.write(self.relay_off)
            self.ser.flush()
            self.ser.close()

if __name__ == '__main__':
    try:
        node = RelayControlNode()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass