from networktables import NetworkTables
from time import sleep

NetworkTables.initialize()

sd = NetworkTables.getTable('SmartDashboard')

sd.putString("wpilib estimated pose w/ ll", "Pose X: 0 Pose Y: 0 Rotation: 0")

while True:
    sleep(2)
