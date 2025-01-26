from pymunk import Body

def keepUpright(body: Body):
	'''Called before physics step to keep a body upright'''
	
	body.angle = 0
	body.angular_velocity = 0 			# Stop the body from rotating