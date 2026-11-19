import importlib.util
import tkinter as tk
import sys
import os

class Pixlz:
	def __init__(self, title:str="Pixlz"):
		self.xres = 20; self.yres = 12

		# general vars
		self.fps = 10
		self.loop = False # loops animation over and over
		self.font = "Courier"
		self.font_size = 12
		self.bg = "black"
		self.fg = "white"
		self.frame_file_prefix = "pxz"
		self.tbox = None

		self.frames = []
		self.current_frame = 0
		self.tags = set()

		self.win = tk.Tk()
		self.win.title(title)

	def config(self,
		xres:int | None = None,
		yres:int | None = None,
		fps:int | None = None,
		loop:bool | None = None,
		font:str | None = None,
		font_size:int | None = None,
		bg:str | None = None,
		fg:str | None = None,
		demo:bool | None = None
	):
		if xres is not None: self.xres = xres
		if yres is not None: self.yres = yres
		if fps is not None: self.fps = fps
		if loop is not None: self.loop = loop
		if font is not None: self.font=font
		if font_size is not None: self.font_size = font_size
		if bg is not None: self.bg = bg
		if fg is not None: self.fg = fg
		if demo is not None:
			if demo is True: self.frame_file_prefix = "example_pxz"

	def _get_frames_dir(self) -> str:
		main_script= os.path.abspath(sys.argv[0])
		cwd = (
			os.path.dirname(main_script)
			if os.path.isfile(main_script)
			else os.getcwd()
		)
		return os.path.join(cwd, "anims")

	def _load_frames(self):
		frames_dir = self._get_frames_dir()
		if not os.path.isdir(frames_dir):
			raise FileNotFoundError(f"Could not find frames dir at: {frames_dir}")
		
		self.frames.clear()
		idx = 0
		while True:
			frame_path = os.path.join(frames_dir, f"{self.frame_file_prefix}{idx}.py")
			if not os.path.exists(frame_path):
				break

			# get frame
			spec = importlib.util.spec_from_file_location(f"{self.frame_file_prefix}{idx}", frame_path)
			module = importlib.util.module_from_spec(spec)
			spec.loader.exec_module(module)

			if hasattr(module, "frame"):
				self.frames.append(module.frame)
			idx += 1

	def init(self):
		self._load_frames()

		# mk text box
		self.tbox = tk.Text(
			self.win,
			width=self.xres,
			height=self.yres,
			font=(self.font, self.font_size),
			bg=self.bg,fg=self.fg,
			padx=0,pady=0,
			borderwidth=0,
			highlightthickness=0,
			wrap="none",
			state="disabled" # no typing
		)

		self.tbox.pack(fill="both", expand=False)
		self.win.resizable(False, False)

	def _render(self, frame):
		# draws current frame onto screen
		self.tbox.config(state="normal")
		self.tbox.delete("1.0", "end")

		rows = []
		for y in range(self.yres):
			row_chars = []
			for x in range(self.xres):
				idx = y * self.xres + x
				if idx < len(frame):
					char = frame[idx][0]
				else:
					char = " "
				row_chars.append(char)
			rows.append("".join(row_chars))
		self.tbox.insert("1.0", "\n".join(rows))

		# give chars colour
		# ln nums 1 indexed, cols 0 indexed
		for y in range(self.yres):
			line_num = y + 1
			for x in range(self.xres):
				idx = y * self.xres + x
				if idx >= len(frame):
					break

				rgb = frame[idx][1]
				hex_colour = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

				# make tag for new colours
				if hex_colour not in self.tags:
					self.tbox.tag_config(hex_colour, foreground=hex_colour)
					self.tags.add(hex_colour)
				
				self.tbox.tag_add(hex_colour, f"{line_num}.{x}", f"{line_num}.{x+1}")
		self.tbox.config(state="disabled")

	def _animate(self):
		if not self.frames: return

		self._render(self.frames[self.current_frame])
		self.current_frame += 1

		if self.current_frame >= len(self.frames):
			if self.loop: self.current_frame = 0
			else: return
		
		delay = max(1, int(1000 / self.fps)) # delay in ms
		self.win.after(delay, self._animate)

	def exec(self):
		if self.tbox is None:
			self.init()
		self._animate()
		self.win.mainloop()