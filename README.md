# Pixhawk Compass Calibration and Waypoint Generation #
This repo contains some testing scripts I used to generate simple paths for testing with the pixhawk system, and also the data processing script for calibrating the pixhawk compass.

## Simple Waypoint Generation ##
The scripts `figure_8_waypoints.py`, `polygons.py`, and `rounded_rect_waypoints.py` generate paths following simple geometries.  `pixhawk.py` contains supporting code for these functions.

## Compass Calibration ##
`ap_log_compass.py`  is used for calibrating a magnetometer for use with Ardupilot.  The Ardupilot system (via MissionPlanner) has compass calibration built in, however the built-in calibration routine is designed for a small vehicle or rover that can be rotate through a full range of roll/pitch/yaw angles, in contrast to a tractor which is rather difficult to tip over!  Essentially, it is appropriate to think of the earth's magnetic field being a needle on a 3d compass and for the calibration procedure you would ideally like the needle to sweep out an entire sphere.  Since the tractor's motion is largely confined to a horizontal plane (both during calibration and otherwise), we accept just sweeping this needle over a circular slice of the full sphere and calibrate on that.

The calibration procedure involves three steps.  Before calibrating, ensure that the magnetometer is installed in a secure location on the tractor, and that the orientation parameters for both the main flight controller (wich has internal IMUs) and the external magnetometer are set correctly.

First, the tractor is driven around in a pattern that will cause one or more full rotations of the magnetic field vector.  I have typically done this by driving in a few tight circles in one direction followed by a few tight circles in the other direction.  Note that having the compass/magnetometer in its final position relative to other ferromagnetic portions of the vehicle is important for the calibration, so it *is* necessary to move the whole vehicle, not just detach the magnetometer from the tractor for calibration.

Second, a log file is downloaded from the Ardupilot system and run through the `ap_log_compass.py` script.  Currently, this requires editing the script to contain the name of the desired file.  There is additional plotting and validation data available in the script that is not output by default but can be enabled by editing the code.

Finally, the outputs from the calibration script are entered into the Ardupilot configuration.  It may be helpful to restart the ardupilot system after the calibration change to reset the EKF.
