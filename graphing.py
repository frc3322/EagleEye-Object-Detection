import matplotlib.pyplot as plt

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Set fixed scale
ax.set_xlim([-10, 10])  # Example scale, adjust as needed
ax.set_ylim([-10, 10])  # Example scale, adjust as needed
ax.set_zlim([-10, 10])  # Example scale, adjust as needed

# Set fixed view
ax.view_init(elev=20, azim=30)  # Example elevation and azimuth, adjust as needed


def plot_3d_point(x, y, z):
    # Plot the new point
    ax.scatter(x, y, z, color='r', s=100)

    # Show plot without freezing
    plt.draw()
    plt.pause(0.001)
