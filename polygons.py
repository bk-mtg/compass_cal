#!/usr/bin/python3

import numpy as np

import pixhawk

def turns(initial_angle=0, n_steps=2, dx=5, dtheta=90):
    x = [0.0]
    y = [0.0]
    theta = initial_angle * np.pi/180
    dtheta = dtheta * np.pi/180
    for i in range(0,n_steps+1):
        dX = [np.cos(theta)*dx, np.sin(theta)*dx]
        x.append(x[-1] + dX[0])
        y.append(y[-1] + dX[1])
        theta += dtheta

    return np.array(x), np.array(y)


if __name__ == '__main__':
    x,y = turns(dx=10, dtheta=45, n_steps=3)
    pixhawk.waypoints_to_file(*pixhawk.meters_to_latlon((x,y), 37.3117874, -120.5088173))
