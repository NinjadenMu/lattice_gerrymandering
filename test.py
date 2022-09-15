
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import colorsys
if __name__ == '__main__':
    print(colorsys.hsv_to_rgb(240, 1 * 0.2, 100))
    print([j for j in range(3) for i in range(3)] * 3)
    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection = '3d')

    x_pos = [1, 1, 1, 2, 2, 2, 3, 3, 3]
    y_pos = [1, 2, 3, 1, 2, 3, 1, 2, 3]
    z_pos = [0] * 9

    dx = [1] * 9
    dy = [1] * 9
    dz = [1] * 9
    ax1.bar3d(x_pos, y_pos, z_pos, dx, dy, dz, color = [(0.9, 0.1, 0.1, 1) for i in range(9)]) 
    plt.show()
