#!/usr/bin/python
# -*- coding: utf-8 -*-

# for launching the app
import subprocess

# for drawing the stuff
import gtk

# for catching the error
import glib

# for reading that stuff
import xdg.Menu
import xdg.DesktopEntry

# for finding that stuff to draw
import xdg.IconTheme

# for finding what stuff to do
import getopt

# for not doing anything anymore
import sys

NAME="xmenud"
VERSION="0.7"
AUTHOR="Matthias Kühlke"
EMAIL="mad@unserver.de"
YEAR="2010"
TAGLINE="A desktop menu, with klickibunti."

def create_menu(menu, depth = 0):
	def launch(widget, string):
		subprocess.Popen(string)

	def get_exec(string):
		return string.split()[0]

	def get_icon(iconname):
		if iconname.find('.')<>-1:
			try:
				pixbuf = gtk.gdk.pixbuf_new_from_file(xdg.IconTheme.getIconPath(iconname))
				ick = gtk.IconSet(pixbuf)
				scaled = ick.render_icon(gtk.Style(), gtk.TEXT_DIR_LTR, gtk.STATE_NORMAL, gtk.ICON_SIZE_LARGE_TOOLBAR, None, None)
				img = gtk.image_new_from_pixbuf(scaled)
			except (TypeError, glib.GError):
				img = gtk.image_new_from_stock(gtk.STOCK_MISSING_IMAGE, gtk.ICON_SIZE_LARGE_TOOLBAR)
		else:
			img = gtk.image_new_from_icon_name(iconname, gtk.ICON_SIZE_LARGE_TOOLBAR)
		return img

	themenu = gtk.Menu()
	for entry in menu.getEntries():
		if isinstance(entry, xdg.Menu.Menu):
			item = gtk.ImageMenuItem(stock_id=entry.getName())
			item.set_image(get_icon(entry.getIcon()))
			submenu = create_menu(entry, depth)
			item.set_submenu(submenu)
			themenu.append(item)
			item.set_tooltip_text(entry.getComment())
			item.show()
		elif isinstance(entry, xdg.Menu.MenuEntry):
			item = gtk.ImageMenuItem(entry.DesktopEntry.getName())
			item.set_image(get_icon(entry.DesktopEntry.getIcon()))
			item.connect("activate", launch, get_exec(entry.DesktopEntry.getExec()))
			themenu.append(item)
			item.set_tooltip_text(entry.DesktopEntry.getComment())
			item.show()
	themenu.show()
	return themenu

def create_popup():
	m=gtk.Menu()
	about = gtk.ImageMenuItem(stock_id=gtk.STOCK_ABOUT)
	quit = gtk.ImageMenuItem(stock_id=gtk.STOCK_QUIT)
	about.connect('activate', lambda w: about_dialog())
	quit.connect('activate', lambda w: gtk.main_quit())
	m.append(about)
	m.append(quit)
	about.show()
	quit.show()
	return m

def about_dialog():
	d = gtk.AboutDialog()
	d.set_name(NAME)
	d.set_version(VERSION)
	d.set_authors(['%s <%s>' % (AUTHOR,EMAIL)])
	d.set_copyright("(c) %s %s" % (YEAR,AUTHOR))
	d.set_modal(False)
	d.run()
	d.destroy()

def tray():
	i = gtk.StatusIcon()
	i.set_from_stock(gtk.STOCK_EXECUTE)
	i.set_tooltip("xmenud")
	i.set_visible(True)
	return i

def main():
	run_tray = False
	try:
		opts, args = getopt.getopt(sys.argv[1:],"htv",["help", "tray", "version"])
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)
	for o, a in opts:
		if o in ('-v', '--version'):
			showversion()
			sys.exit()
		elif o in ('-h', '--help'):
			usage()
			sys.exit()
		elif o in ('-t', '--tray'):
			run_tray = True

	try:
		desktopmenu = xdg.Menu.parse()
	except xdg.Exceptions.ParsingError:
		print 'Parsing error'
		sys.exit(-1)
	
	mainmenu=create_menu(desktopmenu)
	if run_tray:
		popupmenu=create_popup()
		trayicon=tray()
		trayicon.connect("activate", lambda w: mainmenu.popup(None, None, None, 0, 0))
		trayicon.connect("popup-menu", lambda w,b,t: popupmenu.popup(None, None, None, b, t))
	else:
		mainmenu.connect("hide", lambda w: gtk.main_quit())
		mainmenu.popup(None, None, None, 0, 0)
	try:
		gtk.main()
	except KeyboardInterrupt:
		pass
	return 0

def showversion():
	print '%s %s- %s' % (NAME, VERSION, TAGLINE)
	print '(c) %s %s <%s>' % (YEAR, AUTHOR, EMAIL)

def usage():
	print 'usage: %s [--tray|--help] [--version]' % sys.argv[0]

if __name__ == "__main__":
	main()
