#!/usr/bin/python3

import numpy as np
import utm

def figure_8(center=(0,0), angle=0, scale=1):
    s = scale
    ss = s/np.sqrt(2)
    theta_step = s/7*10/4
    lin_step = 5/10*4
    # start at 0,0, move toward first quadrant of turn, at (s,-s)
    x = np.arange(0,ss,lin_step)
    y = np.arange(0,-ss,-lin_step)

    # go three quarters of the way around a circle
    # this circle has it's center at (2s,0), and we run from -3pi/4 to 3pi/4
    theta = np.arange(-np.pi*3/4,np.pi*3/4,np.pi/4/theta_step)
    x = np.concatenate([x, 2*ss + s*np.cos(theta)])
    y = np.concatenate([y, s*np.sin(theta)])

    # straight line to the other circle
    # i.e. from (s,s) to (-s,-s)
    x_ = np.arange(ss,-ss,-lin_step)
    y_ = np.arange(ss,-ss,-lin_step)
    x = np.concatenate([x,x_])
    y = np.concatenate([y,y_])

    # three quarters of the way around that
    # this time we'll go from -7pi/4 to pi/4, and centered at (-2s, 0)
    theta = np.arange(np.pi*7/4, np.pi/4, -np.pi/4/theta_step)
    x_ = -2*ss + s*np.cos(theta)
    y_ = s*np.sin(theta)
    x = np.concatenate([x,x_])
    y = np.concatenate([y,y_])

    # straight line back to the origin
    x_ = np.arange(-ss,0,lin_step)
    y_ = np.arange(ss,0,-lin_step)
    x = np.concatenate([x,x_])
    y = np.concatenate([y,y_])

    # add circle centers
    x_ = np.array([ss,-ss])*2
    y_ = np.array([0,0])
    #x = np.concatenate([x,x_])
    #y = np.concatenate([y,y_])

    # apply rotation and center
    x = x*np.cos(angle) - y*np.sin(angle) + center[0]
    y = y*np.cos(angle) + x*np.sin(angle) + center[1]
    
    return (x,y)

def meters_to_latlon(f8, lat, lon):
    x,y = f8
    (yc,xc,z,t) = utm.from_latlon(lat, lon)
    x = x + xc
    y = y + yc
    r = [utm.to_latlon(xy[0], xy[1], z, t) for xy in zip(y,x)]
    lat, lon = list(zip(*r))
    lat = np.array(lat); lon = np.array(lon)
    return (lat,lon)

def waypoints_to_file(lat, lon):
    print("QGC WPL 110")
    print("0\t1\t0\t16\t0\t0\t0\t0\t{}\t{}\t20\t1".format(lat[0],lon[0]))
    for i,lat_ in enumerate(lat):
        print("{}\t0\t3\t16\t0\t0\t0\t0\t{}\t{}\t1\t1".format(i+1, lat_, lon[i]))

if __name__ == '__main__':
    x,y = figure_8(scale=13.1)
    latlon = meters_to_latlon((x,y), 37.3119437, -120.509202)
    waypoints_to_file(latlon[0],latlon[1])
