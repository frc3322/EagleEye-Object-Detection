from networktables import NetworkTables

NetworkTables.initialize()

sd = NetworkTables.getTable('SmartDashboard')

sd.putString("wpilib estimated pose w/ ll", "Pose X: 0 Pose Y: 0 Rotation: 0")

while True:
    print(sd.getString("notes", "None"))
