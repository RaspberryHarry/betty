def report(action, zeige):
	show = zeige				

	if show == 1:
		print action
		return True
	else:
		return False


def copy_array(array, wert):
	new_one = array.copy()
	for key, value in array.iteritems():
		new_one[key] = wert

	return new_one
