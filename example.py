import pixlz

anim = pixlz.Pixlz(title="Squid")
anim.config(
	fps=5,
	loop=True,
	demo=True # do not use in your animation. changes expected frame file name
)
anim.exec()