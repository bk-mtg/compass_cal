import re
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def read_ap_log(filename):
	data = {'FMT': {}}
	with open(filename) as f:
		for line in f:
			fields = re.split(', *', line);
			type = fields.pop(0);
			if type == "FMT":
				type = fields[2];
				fields = fields[4:];
				data['FMT'][type] = fields;
			elif type in data:
				data[type].append(fields)
			else:
				data[type] = [fields]
	for field in data:
		lengths = np.unique([len(x) for x in data[field]])
		if len(lengths) != 1:
			print("unable to rotate field", field)
			continue
		local_data = np.transpose(data[field])
		try:
			local_data = local_data.astype(float);
		except:
			pass
		data[field] = dict(zip(data['FMT'][field], local_data))
	return data

def plot_mag(mag):
	plt.figure();
	plt.plot(mag['TimeUS'], mag['MagX'])
	plt.plot(mag['TimeUS'], mag['MagY'])
	plt.plot(mag['TimeUS'], mag['MagZ'])

def plot_mag_3d(mag, ax=None):
	if ax is None:
		fig = plt.figure();
		ax = fig.add_subplot(111, projection='3d')
	ax.scatter3D(mag['MagX'], mag['MagY'], mag['MagZ'])
	return ax

def plot_mag_circles_3d(data):
	ax = plot_mag_3d(data['MAG'])
	plot_mag_3d(data['MAG2'], ax)
	plot_mag_3d(data['MAG3'], ax)

def plot_mag_circles(data):
	mag1 = data['MAG']
	mag2 = data['MAG2']
	mag3 = data['MAG3']
	plt.figure();
	plt.plot(mag1['MagX'],mag1['MagZ'], mag2['MagX'],mag2['MagY'], mag3['MagX'], mag3['MagY'])

def determine_plane_rotation(mag):
	r = np.linalg.lstsq(np.transpose([mag['MagX'], mag['MagY'], mag['MagZ']]), np.ones([len(mag['MagX']), 1]), rcond=None)
	r = r[0] # just the fit results please
	r = r/math.sqrt(sum(r*r))
	return r

def rotation_matrix(axis, theta):
	"""
	Return the rotation matrix associated with counterclockwise rotation about
	the given axis by theta radians.
	http://en.wikipedia.org/wiki/Euler–Rodrigues_formula
	https://stackoverflow.com/questions/6802577/rotation-of-3d-vector/6802723#6802723
	"""
	axis = np.asarray(axis)
	axis = axis / math.sqrt(sum(axis*axis))
	a = math.cos(theta / 2.0)
	b, c, d = -axis * math.sin(theta / 2.0)
	aa, bb, cc, dd = a * a, b * b, c * c, d * d
	bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
	return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
	                 [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
	                 [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

def rotation_up(vec):
	up = [0,0,1]
	vec = np.transpose(vec)
	axis = np.cross(vec, up)
	theta = math.acos(np.dot(vec, up))
	# temporary hack for not doing a very good job here:
	if theta < 0.1:
		theta = 0
	elif theta > 0.9:
		print("WARNING: looks like your orientation might be off?")
	return rotation_matrix(np.transpose(axis), theta)

def plot_mag_rotated(mag, ax=None, inclination=61):
	# compute rotation and re-orient so that we have a circle at constant Z
	r = determine_plane_rotation(mag);
	R = rotation_up(np.transpose(r)[0])
	new_mag = R @ [mag['MagX'], mag['MagY'], mag['MagZ']]
	# determine the center of the circle
	xM = max(new_mag[0]); xm = min(new_mag[0])
	xr = (xM-xm)/2; xc = (xM+xm)/2
	yM = max(new_mag[1]); ym = min(new_mag[1])
	yr = (yM-ym)/2; yc = (yM+ym)/2
	zC = sum(new_mag[2])/len(new_mag[2])
	# add a scale to keep xr == yr by adjusting yr
	S = np.array([[1,0,0], [0,xr/yr, 0], [0,0,1]])
	
	# assume the z coordinate should be given by the inclination
	inclination = inclination*np.pi/180
	zc = xr * np.tan(inclination)
	if zC < 0:
		zc = -zc
	zc = zC-zc
	
	# pass the center coordiantes backward through the rotation to get the original offsets
	Xc1 = np.linalg.inv(R) @ np.array([[xc],[yc],[zc]])
	Xc = np.linalg.inv(R) @ np.array([[xc],[yc],[zC]])
	zc = xr * np.tan(inclination)
	if Xc[2] < 0:
		zc = -zc
	Xc[2] = Xc[2]-zc
	
	# and make a plot
	new_mag2 = (S @ R) @ [mag['MagX']-Xc1[0], mag['MagY']-Xc1[1], mag['MagZ']-Xc1[2]]
	new_mag3 = S @ [mag['MagX']-Xc[0], mag['MagY']-Xc[1], mag['MagZ']-Xc[2]]
	new_mag = new_mag2
	new_mag = dict(zip(('MagX', 'MagY', 'MagZ'), new_mag))
	ax = plot_mag_3d(mag)
	plot_mag_3d(new_mag, ax)
	new_mag = dict(zip(('MagX', 'MagY', 'MagZ'), new_mag3))
	plot_mag_3d(new_mag, ax)

	return (S, R, Xc, new_mag)

def get_parm_dict(data):
	return dict(zip(data['PARM']['Name'], data['PARM']['Value\n']))

def print_cal(S, Xc, number, params):
	if number is None:
		number = ''
	else:
		number = str(number)
	if np.shape(Xc) == (3,1):
		Xc = np.transpose(Xc)[0]
		
	root = 'COMPASS_OFS' + number + '_'
	dia = 'COMPASS_DIA'+number+'_'
	oldxc = np.array([params[root+'X'], params[root+'Y'], params[root+'Z']]).astype(float)
	olddia = np.array([params[dia+'X'], params[dia+'Y'], params[dia+'Z']]).astype(float)
	if not all(olddia == 1):
		print("WARNING: operating with old scaling present not well tested\n")
		# scale appropriately
		Xc = Xc/olddia
		S = np.diag(S @ (1/olddia))
	print(root+'X:', -Xc[0]+oldxc[0], root+'Y:', -Xc[1]+oldxc[1], root+'Z:', -Xc[2]+oldxc[2])
	print(dia+'X:', S[0][0], dia+'Y', S[1][1], dia+'Z', S[2][2])
	print('COMPASS_ODI'+number+'_{X,Y,Z} = 0')

def calibrate(filename):
	data = read_ap_log(filename);
	print('Calibration for', filename)
	
	parameters = get_parm_dict(data)
	print('Magnetometer 1 calibration:')
	(S, R, Xc, new_mag) = plot_mag_rotated(data['MAG'])
	print_cal(S, Xc, '', parameters)
	print('Magnetometer 2 calibration:')
	(S, R, Xc, new_mag) = plot_mag_rotated(data['MAG2'])
	print_cal(S, Xc, '2', parameters)
	print('Magnetometer 3 calibration:')
	(S, R, Xc, new_mag) = plot_mag_rotated(data['MAG3'])
	print_cal(S, Xc, '3', parameters)


if __name__ == '__main__':
	calibrate('2018-11-05 12-39-01.log');
	exit();
	
	plt.ion()
	
	mag1 = data['MAG']
	mag2 = data['MAG2']
	mag3 = data['MAG3']
	gps = data['GPS2']
	att = data['ATT']
	mag_decl = 13 ; # looked up with USGS for the test site
	
	# check that GPS GCrs data matches the expected conventions
	gpsangle = np.arctan2(np.diff(gps['Lat']),np.diff(gps['Lng']))*180/np.pi
	gpsangle = np.mod(90-gpsangle, 360)
	plt.plot(gps['TimeUS'][1:], gpsangle, gps['TimeUS'], gps['GCrs'])
	# yeah, it's pretty good.  next...
	
	plot_mag(mag1);
	plot_mag(mag2);
	plot_mag(mag3);
	
	# look, circles:
	plot_mag_circles(data)
	
	# let's try deciphering mag1, arbitrarily, not being fancy and elliptical:
	mag1x = (mag1['MagX']+28.5)/(190+247) # graphically determined
	mag1z = (mag1['MagZ']+273)/(-46+500) # graphically determined again
	magangle = np.arctan2(mag1x, mag1z)*180/np.pi
	# just for fun, mag2 and mag3 as well:
	mag2x = (mag2['MagX']+101.5)/(127+330) # graphically determined
	mag2y = (mag2['MagY']+175)/(-17+333) # graphically determined again
	mag3x = (mag3['MagX']-10.5)/(185+164) # graphically determined
	mag3y = (mag3['MagY']+427)/(-273+581) # graphically determined again
	magangle2 = 90-np.arctan2(mag2y, mag2x)*180/np.pi - 90 + mag_decl
	magangle3 = 90-np.arctan2(mag3y, mag3x)*180/np.pi - 90 + mag_decl
	#plot it!
	plt.figure();
	plt.plot(mag3['TimeUS'], np.mod(magangle3, 360), label='Manual Magnetometer Heading (int3)');
	plt.plot(mag2['TimeUS'], np.mod(magangle2, 360), label='Manual Magnetometer Heading (int2)');
	plt.plot(mag1['TimeUS'], np.mod(magangle-75,360), label='Manual Magnetometer Heading (ext)')
	plt.plot(gps['TimeUS'], gps['GCrs'], label='GPS Ground Course');
	plt.plot(att['TimeUS'], att['Yaw'], label='ATT Yaw');
	plt.plot(data['AHR2']['TimeUS'], data['AHR2']['Yaw'], label='AHRS Yaw');
	plt.legend()
	plt.ylabel('Heading (degrees cw from N)')
	plt.xlabel('Time [μs]')
