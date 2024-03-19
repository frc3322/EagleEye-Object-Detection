from networktables import NetworkTables
from time import sleep

NetworkTables.initialize()

sd = NetworkTables.getTable("SmartDashboard")

sd.putString("wpilib estimated pose w/ ll", "Pose X: 0 Pose Y: 0 Rotation: 0")


def valueChanged(table, key, value, isNew):
    print("valueChanged: key: '%s'; value: %s; isNew: %s" % (key, value, isNew))


def connectionListener(connected, info):
    print(info, "; Connected=%s" % connected)


NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

sd.addEntryListener(valueChanged)


while True:
    sleep(1)
