import traceback, os, sys, time, pygame, mymodule as my, RPi.GPIO as gpio

zeige_report = 1
controllerLostLoops = 20			# Nach 20 Intervallen wird unterstellt, dass der Controller verloren ist
interval = 0.01						# reaktionsgeschwindigkeit
read = { "X": 9, "O": 13, "Start": 3, "Select": 0, "LeftRight": 0, "UpDown": 1 }						# Einstellbar
read_axis = [ "LeftRight", "UpDown" ]

# GPIO Ports
led = { "power": 7, "forward": 11, "backward": 13 }
pwm = { "forward": 0, "backward": 0 }
frequenz = 100

## dont change ###########################
interval_long = 10  	## primary during dev to get the chance to read
loop = 1				## just a counter
return_data = my.copy_array(read, 0)
###########################################


# GPIO ####################################
gpio.setmode(gpio.BOARD)

for key, value in led.iteritems():
	if key in pwm:
		gpio.setup(value, gpio.OUT)
		pwm[key] = gpio.PWM(value, frequenz)
		pwm[key].start(0)
	else:
		gpio.setup(value, gpio.OUT)
		gpio.output(value, False)


try:
	try:
		my.report ("--- init ---", zeige_report)
		pygame.init()
		pygame.joystick.init()

		if pygame.joystick.get_count() < 1:
			pygame.joystick.quit()
			my.report ("No Controller found!", zeige_report)
			joystick = False

		else:
			joystick = pygame.joystick.Joystick(0)
			my.report ("Controller found!", zeige_report)

		time.sleep(1)


		joystick.init()
	except:
		print "Fehler beim initialisieren des Gamepads!"

	print " ___________________________ "
	print "|    Bitte Start drucken    |"
	print "|   Select zum abschalten   |"
	print "|___________________________|"

	running = True
	loopsWithoutEvent = 0
	controllerLost = False
	power_on = False

	##############################################################################

	status = True
	while running:

		hinweis = "======================"

		my.report(">>>>>>>>>>> ", zeige_report)
		my.report(">>> Running ", zeige_report)
		
########

		for event in pygame.event.get():

			for key, value in read.iteritems():
				#my.report("==============", zeige_report)
				#my.report(loop, zeige_report)

				if key in read_axis:
					#my.report("- Axis:      " + key, zeige_report)
					return_data[key] = joystick.get_axis(value)
				else:
					#my.report("- Button:    " + key, zeige_report)
					return_data[key] = joystick.get_button(value)

			loop += 1

			if power_on:
				RichtungUpDown = return_data["UpDown"]*100

				if RichtungUpDown == 0:
					pwm["forward"].ChangeDutyCycle(100)
					pwm["backward"].ChangeDutyCycle(100)
				elif RichtungUpDown < 0:
					pwm["forward"].ChangeDutyCycle(RichtungUpDown*-1)
					pwm["backward"].ChangeDutyCycle(0)
					hinweis = "=== " + str(RichtungUpDown)
				else:
					pwm["forward"].ChangeDutyCycle(0)
					pwm["backward"].ChangeDutyCycle(RichtungUpDown)
					hinweis = "=== " + str(RichtungUpDown)
			else:
				pwm["forward"].ChangeDutyCycle(0)
				pwm["backward"].ChangeDutyCycle(0)	

			if return_data["Start"] == 1:
				gpio.output(led["power"], True)
				power_on = True
				hinweis = "======= Power an ============"
			elif return_data["Select"] == 1:
				gpio.output(led["power"], False)
				power_on = False
				hinweis = "======= Power aus ==========="


		my.report(hinweis, zeige_report)
		time.sleep(interval)

	##############################################################################


except KeyboardInterrupt:
	# CTRL+C exit, disable all drives
	print "\n"
	print " ___________________________ "
	print "| User shutdown             |"
	print "|___________________________|"
	#MOTOR

except:
	print "\n"
	print " _______________________________________________ "
	print "| Unbekannter Fehler                            |"
	print "| Meldung:                                      |"
	print (traceback.print_exc())

finally:
	###
	print "Beendet"
	gpio.cleanup()

