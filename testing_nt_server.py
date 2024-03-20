from networktables import NetworkTables
from time import sleep

NetworkTables.initialize()

sd = NetworkTables.getTable("SmartDashboard")

sd.putString("wpilib estimated pose w/ ll", "Pose X: 0 Pose Y: 0 Rotation: 0")


def value_changed(table, key, value, is_new):
    print("valueChanged: key: '%s'; value: %s; isNew: %s" % (key, value, is_new))


def connection_listener(connected, info):
    print(info, "; Connected=%s" % connected)


NetworkTables.addConnectionListener(connection_listener, immediateNotify=True)

sd.addEntryListener(value_changed)


while True:
    sleep(1)
