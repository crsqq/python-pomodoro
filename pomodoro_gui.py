#!/usr/bin/env python3
# encoding: utf-8

from gi.repository import Gtk, Notify, GObject

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import time
import threading
import os

class PomodoroGui:
    def __init__(self):
        self.gladfile = "pomodoro.glade"
        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladfile)

        #magic
        self.builder.connect_signals(self)

        self.window = self.builder.get_object("root_window")
        #self.aboutdialog = self.builder.get_object("aboutdialog1")
        #self.statusbar = self.builder.get_object("statusbar1")
        #self.context_id = self.statusbar.get_context_id("status")

        #time left label
        self.time_left = self.builder.get_object("time_left_label")
        self.time_left.set_text("not running")

        #text entry box for timer duration
        self.timer_value = self.builder.get_object("timer_entry")
        self.timer_value.set_text("1")

        #run button

        self.pomodoro_timer = PomodoroTimer()
        self.pomodoro_timer.register_running_callback(self.timer_on_off_callback)
        self.pomodoro_timer.register_time_left_callback(self.time_left_callback)

        self.window.show()

    def on_root_window_destroy(self, object, data=None):
        logging.debug("quit with cancel")
        Gtk.main_quit()


    def on_gtk_quit_activate(self, menuitem, data=None):
        logging.debug("quit from menu")
        Gtk.main_quit()


    def on_gtk_about_activate(self, menuitem, data=None):
        logging.debug("help about selected")
        self.response = self.aboutdialog.run()
        self.aboutdialog.hide()

    def on_button_run_clicked(self, button, data=None):

        timer_value = self.builder.get_object("timer_entry")
        #TODO validate input
        try:
            timer_value = float(timer_value.get_text()) * 60
        except Exception as e:
            #fixme
            raise e

        self.pomodoro_timer.start(timer_value)

    def on_button_cancel_clicked(self, button, data=None):
        self.pomodoro_timer.running = False


    #callbacks
    def timer_on_off_callback(self, is_now_running):
        """
        disables / enables ui component based on the status of the PomodoroTimer
        """
        logging.debug("is_now_running %s" % is_now_running)

        button_run = self.builder.get_object("button_run")
        if(is_now_running):
            GObject.idle_add(lambda: button_run.set_sensitive(False))
        else:
            GObject.idle_add(lambda: button_run.set_sensitive(True))

    def time_left_callback(self, time_left):
        logging.debug("time_left: %s" % time_left)
        #TODO format time properly
        self.time_left.set_text("%02.0f:%02.0f" % (time_left //60, time_left % 60 ))


class PomodoroTimer:
    def __init__(self):
        self._running = False
        self.running_callbacks = []

        self._time_left = 0
        self.time_left_callbacks = []

    def start(self, duration):
        self.time_left = duration
        thr = threading.Thread(target=self.make_notification, args=(duration,))
        thr.daemon = True
        thr.start()

    def make_notification(self, duration):
        self.running = True
        while(self.time_left > 0):
            if(not self.running):
                return False
            time.sleep(1)
            self.time_left -= 1

        Notify.init("pomodoro.py")
        main_text = "Time is up."
        summary_text = "summary text"

        notification = Notify.Notification.new(main_text, summary_text, None)
        notification.show()
        os.system("espeak 'Time is up.'")
        self.running = False


    @property
    def running(self):
        print("running getter called")
        return self._running

    @running.setter
    def running(self, value):
        self._running = value
        for callback in self.running_callbacks:
            callback(self._running)

    def register_running_callback(self, callback):
        """
        callback(bool running): function that is called when 'running' changes its value
        """
        if callback not in self.running_callbacks:
            self.running_callbacks.append(callback)

    @property
    def time_left(self):
        return self._time_left

    @time_left.setter
    def time_left(self, new_time):
        self._time_left = new_time
        for callback in self.time_left_callbacks:
            callback(self._time_left)

    def register_time_left_callback(self, callback):
        """
        callback(float time_left): function that is called when 'time_left' changes its value
        """
        if callback not in self.time_left_callbacks:
            self.time_left_callbacks.append(callback)


if __name__ == "__main__":
    GObject.threads_init()
    main = PomodoroGui()
    Gtk.main()
