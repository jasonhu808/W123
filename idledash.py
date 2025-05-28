import tkinter as Tkinter
import PIL 
import math	# Required For Coordinates Calculation
import time
import PIL.Image
import PIL.ImageEnhance
import PIL.ImageTk	# Required For Time Handling
import cv2

#
#
# class
class idledash(Tkinter.Tk):
	def __init__(self):

		self.angle = 55

		Tkinter.Tk.__init__(self)


		self.length=90	# Stick Length
		self.tach_stick_length = 200


		self.cx, self.cy = 350, 400  # assume center of your screen (or use your own)

		#defining all spacial variables
		self.welcome_X=self.cx
		self.welcome_Y=self.cy


		## Tach Image Rotation
		tach_x, tach_y = self.cx, self.cy-220
		# Get the true XY position to use with anchor='center'
		self.true_tach_x, self.true_tach_y = self.rotate_point_backwards(tach_x, tach_y, self.cx, self.cy, self.angle)

		## Tach Needle Rotation, +3 and +110 because the tach.GIF image is not exactly centered
		needle_x, needle_y = tach_x+4, tach_y+110
		# Get the true XY position to use with anchor='center'
		self.true_needle_x, self.true_needle_y = self.rotate_point_backwards(needle_x, needle_y, self.cx, self.cy, self.angle)

		## Clock Image Rotation cx+7 because images are not exactly centered
		clock_x, clock_y = self.cx+7, 600
		self.true_clock_x, self.true_clock_y = self.rotate_point_backwards(clock_x, clock_y, self.cx, self.cy, self.angle)

		## Batt Volt text location rotation
		batt_v_x, batt_v_y = self.cx-250, 400
		self.battV_X, self.battV_Y = self.rotate_point_backwards(batt_v_x, batt_v_y, self.cx, self.cy, self.angle)

		## Coolant Temp text location rotation
		cool_t_x, cool_t_y = self.cx+250, 400
		self.coolT_X, self.coolT_Y = self.rotate_point_backwards(cool_t_x, cool_t_y, self.cx, self.cy, self.angle)

		## CPU Temp text location rotation
		cpu_t_x, cpu_t_y = self.cx, self.cy
		self.cpuT_X, self.cpuT_Y = self.rotate_point_backwards(cpu_t_x, cpu_t_y, self.cx, self.cy, self.angle)

		## Shift text location rotation
		shift_x, shift_y = self.cx, self.cy-75
		self.true_shift_x, self.true_shift_y = self.rotate_point_backwards(shift_x, shift_y, self.cx, self.cy, self.angle)


		self.create_canvas_for_shapes()
		self.alpha = 0.0
		self.increasing = True
		self.overrideredirect(True)
		self.config(cursor="none")
		self.cap = cv2.VideoCapture(0)  # Open the default camera

	# Creating Trigger For Other Functions
	def creating_all_function_trigger(self):
		self.creating_background_()
		self.creating_sticks()
		return


	# Creating Background
	def creating_background_(self):
		self.canvas.delete("all")

		# Load, rotate, and place the image
		self.tach = PIL.Image.open('/home/jhu/Desktop/tach.GIF')
		self.tach = self.tach.rotate(self.angle, expand=True)
		self.tach_tk = PIL.ImageTk.PhotoImage(self.tach)
		self.canvas.create_image(self.true_tach_x, self.true_tach_y, image=self.tach_tk, anchor="center")


		self.clock = PIL.Image.open('/home/jhu/Desktop/clock2.PNG')
		self.clock = self.clock.rotate(self.angle, expand=True)
		self.clock_tk = PIL.ImageTk.PhotoImage(self.clock)
		self.canvas.create_image(self.true_clock_x, self.true_clock_y, image=self.clock_tk, anchor="center")


		self.battV = self.canvas.create_text(
			self.battV_X, self.battV_Y,
			text="Batt. Volt.\n...V",
			angle=self.angle,
			fill="white",
			font=('Helvetica', 16),
			anchor="center",
			justify="center"
		)

		self.coolT = self.canvas.create_text(
			self.coolT_X, self.coolT_Y,
			text="Cool. Temp.\n ...C",
			angle=self.angle,
			fill="white",
			font=('Helvetica', 16),
			anchor="center",
			justify="center"
		)

		self.CPUT = self.canvas.create_text(
			self.cpuT_X, self.cpuT_Y,
			text="CPU Temp.\n...F",
			angle=self.angle,
			fill="white",
			font=('Helvetica', 16),
			anchor="center",
			justify="center"
		)

		self.shift = self.canvas.create_text(
			self.true_shift_x, self.true_shift_y,
			text="SHIFT",
			angle=self.angle,
			fill="black",
			font=('Helvetica', 18),
			anchor="center",
			justify="center"
		)
		# self.coolT = self.canvas.create_text(self.coolT_X, self.coolT_Y,text="Coolant Temp.\n 95C",angle=self.angle, fill="white", font=('Helvetica', 16))
		return
	
	def update_batt_v(self, voltage):
		self.canvas.itemconfig(self.battV, text="Batt. Volt.\n" + str(voltage) + "V")
		return
	
	def update_cool_f(self, coolF):
		# self.coolT.config(text=f"Coolant Temp.\n {coolF}F")
		return
	
	def update_cpu_t(self, cpuT):
		self.canvas.itemconfig(self.CPUT, text="CPU Temp.\n" + str(cpuT) + "F")
		return
	
	def show_shift(self, color):
			self.canvas.itemconfig(self.shift, fill=color)
			return
	
	
	def welcome_screen_(self):
		# Delete the previous image (if any) to free up memory
		self.image2 = None
		
		# Open the MBZ2.png image and apply brightness enhancement
		self.image2 = PIL.Image.open('/home/jhu/Desktop/MBZ3.PNG')
		self.image2 = self.image2.rotate(self.angle, expand=True)
		brightness_factor = 1.0 if self.alpha > 1.0 else self.alpha
		self.faded_image = PIL.ImageEnhance.Brightness(self.image2).enhance(brightness_factor)

		# Convert the faded image to a Tkinter-compatible format and display it
		self.image = PIL.ImageTk.PhotoImage(self.faded_image)
		self.canvas.create_image(self.welcome_X, self.welcome_Y, image=self.image)

		# Update the alpha value
		self.alpha_last = self.alpha
		self.alpha += 0.05 if self.increasing else -0.05

		# Reverse the direction of the alpha fade if it exceeds bounds
		if self.alpha >= 1.7:
			self.increasing = False
		elif self.alpha <= 0.0:
			self.increasing = True

	
	# creating Canvas
	def create_canvas_for_shapes(self):

		self.canvas=Tkinter.Canvas(self, bg='black')
		self.canvas.pack(expand='yes',fill='both')
		self.canvas.config(width=800, height=800)
		return


	# Creating Moving Sticks
	#Second hand is index 2
	#Minute hand is index 1
	#Hour hand is index 0
	def creating_sticks(self):
		self.sticks = []
		for i in range(2):  # Hour and minute hands only
			if i == 0:  # Hour hand
				length = self.length - 10
				width = 5
				color = 'orange'
			elif i == 1:  # Minute hand
				length = self.length
				width = 5
				color = 'orange'

			# Create triangle (pointer shape) pointing straight up initially
			points = [
				self.true_clock_x, self.true_clock_y,  # base center
				self.true_clock_x - width / 2, self.true_clock_y + 10,  # left base
				self.true_clock_x + width / 2, self.true_clock_y + 10,  # right base
				self.true_clock_x, self.true_clock_y - length  # tip of the pointer
			]
			hand = self.canvas.create_polygon(points, fill=color, outline=color)
			self.sticks.append(hand)

		# Create tach needle as a triangle (sharp pointer)
		tach_width = 10  # Make it thinner than clock hands
		tach_length = self.tach_stick_length

		tach_points = [
			self.true_needle_x, self.true_needle_y - tach_length,  # Tip
			self.true_needle_x - tach_width / 2, self.true_needle_y,  # Left base
			self.true_needle_x + tach_width / 2, self.true_needle_y   # Right base
		]

		self.tach_stick = self.canvas.create_polygon(tach_points, fill='red', outline='red')
		
		return
	
	def update_tach(self, raw_value):
		max_rpm = 4500  # Example max RPM
		angle_range = 180  # Full sweep from left to right
		zero_angle = -180-self.angle  # Leftmost position (0 RPM)

		# Convert raw RPM value to angle
		angle_deg = zero_angle + (raw_value / max_rpm) * angle_range
		angle_rad = math.radians(angle_deg)

		# Define needle size
		tach_width = 5  # Thin width for the needle
		tach_length = self.tach_stick_length

		# Calculate rotated tip position
		tip_x = self.true_needle_x + tach_length * math.cos(angle_rad)
		tip_y = self.true_needle_y + tach_length * math.sin(angle_rad)

		# Calculate base positions
		base_angle1 = angle_rad + math.pi / 2
		base_angle2 = angle_rad - math.pi / 2

		base1_x = self.true_needle_x + (tach_width / 2) * math.cos(base_angle1)
		base1_y = self.true_needle_y + (tach_width / 2) * math.sin(base_angle1)

		base2_x = self.true_needle_x + (tach_width / 2) * math.cos(base_angle2)
		base2_y = self.true_needle_y + (tach_width / 2) * math.sin(base_angle2)

		# Update tach needle shape
		self.canvas.coords(self.tach_stick, tip_x, tip_y, base1_x, base1_y, base2_x, base2_y)
		return


	def update_class(self):
		now = time.localtime()
		hour = (now.tm_hour % 12) * 5  # Convert to clock-like scale
		now = (hour, now.tm_min, now.tm_sec)

		for n, i in enumerate(now[:2]):  # Hour and minute hands
			angle_deg = i * 6 - 90 - self.angle  # Rotate counter-clockwise 55°
			angle_rad = math.radians(angle_deg)

			if n == 0:
				length = self.length - 25
				width = 10
			elif n == 1:
				length = self.length
				width = 6

			# Tip of the hand
			tip_x = self.true_clock_x + length * math.cos(angle_rad)
			tip_y = self.true_clock_y + length * math.sin(angle_rad)

			# Two base corners
			base_angle1 = angle_rad + math.pi / 2
			base_angle2 = angle_rad - math.pi / 2

			base1_x = self.true_clock_x + (width / 2) * math.cos(base_angle1)
			base1_y = self.true_clock_y + (width / 2) * math.sin(base_angle1)

			base2_x = self.true_clock_x + (width / 2) * math.cos(base_angle2)
			base2_y = self.true_clock_y + (width / 2) * math.sin(base_angle2)

			points = [tip_x, tip_y, base1_x, base1_y, base2_x, base2_y]
			self.canvas.coords(self.sticks[n], *points)


	def show_reverse_feed(self):
		ret, frame = self.cap.read()
		if ret:
			# Resize the frame to match the canvas
			frame = cv2.resize(frame, (800, 800))
			rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			pil_image = PIL.Image.fromarray(rgb_image)

			# 🔄 Rotate 55 degrees CCW (expand=True keeps the full image visible)
			pil_image = pil_image.rotate(self.angle, expand=True)

			tkinter_image = PIL.ImageTk.PhotoImage(pil_image)

			self.canvas.delete("rev_feed")
			self.canvas.create_image(self.cx, self.cy, anchor="center", image=tkinter_image, tags="rev_feed")
			self.canvas.tag_raise("rev_feed")

			self.canvas.image = tkinter_image  # Prevent garbage collection

			
	
	def hide_reverse_feed(self):
		self.canvas.delete("rev_feed")


	def rotate_point_backwards(self, x_rotated, y_rotated, center_x, center_y, angle_deg):
		angle_rad = math.radians(angle_deg)

		# Translate point to origin
		dx = x_rotated - center_x
		dy = y_rotated - center_y

		# Apply reverse rotation
		x_unrot = dx * math.cos(-angle_rad) - dy * math.sin(-angle_rad)
		y_unrot = dx * math.sin(-angle_rad) + dy * math.cos(-angle_rad)

		# Translate back to global coordinates
		x_original = x_unrot + center_x
		y_original = y_unrot + center_y

		return x_original, y_original


