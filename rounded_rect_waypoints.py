#!/usr/bin/python3

import numpy as np
import utm

def rounded_rect(length=10, height=10, r=2, angle=0):
    length -= 2*r; l=length
    height -= 2*r; h=height
    if(length<0 or height<0):
        raise ValueError('radius too large for length/height')
    theta_step = np.pi/2/5
    lin_step = 1.5
    # start at the back left corner, i.e. (-length, 0)
    x = np.arange(-length, 0, lin_step)
    y = 0*x

    # quarter circle centered at (0,r)
    theta = np.arange(-np.pi/2,0,theta_step)
    x_ = 0 + r*np.cos(theta)
    y_ = r + r*np.sin(theta)
    x = np.concatenate([x,x_])
    y = np.concatenate([y,y_])

    # straight line at x=r from y=r to y=r+h
    y_ = np.arange(r,r+h,lin_step)
    x_ = y_*0 + r
    x = np.concatenate([x,x_])
    y = np.concatenate([y,y_])

    # corner centered at (0, r+h)
    theta = np.arange(0, np.pi/2, theta_step)
    x_ = 0 + r*np.cos(theta)
    y_ = r+h + r*np.sin(theta)
    x = np.concatenate([x,x_])
    y = np.concatenate([y,y_])

    # straight line along the top side; y=h+2r, x from 0 to -length
    x_ = np.arange(0, -length, -lin_step)
    y_ = x_*0 + h + 2*r
    x = np.concatenate([x,x_])
    y = np.concatenate([y,y_])

    # corner centered at (-l, r+h)
    theta = np.arange(np.pi/2, np.pi, theta_step)
    x_ = -length + r*np.cos(theta)
    y_ = r + height + r*np.sin(theta)
    x = np.concatenate([x,x_])
    y = np.concatenate([y,y_])
    
    # down the back side
    y_ = np.arange(r+h,r,-lin_step)
    x_ = y_*0 - l -r
    x = np.concatenate([x,x_])
    y = np.concatenate([y,y_])

    # last corner back to the start point
    theta = np.arange(np.pi, np.pi*3/2, theta_step)
    x_ = -length + r*np.cos(theta)
    y_ = r + r*np.sin(theta)
    x = np.concatenate([x,x_])
    y = np.concatenate([y,y_])

    # apply rotation
    x = x*np.cos(angle) - y*np.sin(angle)
    y = y*np.cos(angle) + x*np.sin(angle)
    
    return (x,y)

def meters_to_latlon(f8, lat, lon):
    x,y = f8
    (easting,northing,z,t) = utm.from_latlon(lat, lon)
    x = x + easting
    y = y + northing
    r = [utm.to_latlon(xy[0], xy[1], z, t) for xy in zip(x,y)]
    lat, lon = list(zip(*r))
    lat = np.array(lat); lon = np.array(lon)
    return (lat,lon)

def waypoints_to_file(lat, lon):
    print("QGC WPL 110")
    print("0\t1\t0\t16\t0\t0\t0\t0\t{}\t{}\t20\t1".format(lat[0],lon[0]))
    for i,lat_ in enumerate(lat):
        print("{}\t0\t3\t16\t0\t0\t0\t0\t{}\t{}\t1\t1".format(i+1, lat_, lon[i]))

if __name__ == '__main__':
    x,y = rounded_rect(height=800*25.4/1000, length=60, r=7, angle=np.arctan(1.3/50))
    latlon = meters_to_latlon((x,y), 37.3117874, -120.5088173)
    waypoints_to_file(latlon[0],latlon[1])
