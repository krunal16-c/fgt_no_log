"""
File Name: event_logger.py

Authors: Kyle Seidenthal

Date: 12-06-2020

Description: Module for logging user interaction events.

"""
import logging
import time
import datetime


class EventLogger():
    """
    For logging user interactions.

    """

    def __init__(self):
        self._event_logger = logging.getLogger('event_logger')

        self._active_tool = "None"

    @property
    def active_tool(self):
        return self._active_tool

    @active_tool.setter
    def active_tool(self, value):
        tool_id = value.lower()
        tool_id = tool_id.replace(" ", "_")

        self._active_tool = tool_id

    def add_handler(self, handler):
        self._event_logger.addHandler(handler)

    def log_load_image(self, image_filename, image_width, image_height,
                       patch_grid_width, patch_grid_height):

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        event_data = {}
        event_data['event_type_id'] = "load_image"
        event_data['timestamp'] = st
        event_data['image_filename'] = image_filename
        event_data['image_width'] = image_width
        event_data['image_height'] = image_height
        event_data['patch_grid_width'] = patch_grid_width
        event_data['patch_grid_height'] = patch_grid_height

        self._event_logger.info(event_data)

    def log_load_mask(self, image_filename, image_width, image_height,
                      patch_grid_width, patch_grid_height):

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        event_data = {}
        event_data['event_type_id'] = "load_mask"
        event_data['timestamp'] = st
        event_data['image_filename'] = image_filename
        event_data['image_width'] = image_width
        event_data['image_height'] = image_height
        event_data['patch_grid_width'] = patch_grid_width
        event_data['patch_grid_height'] = patch_grid_height

        self._event_logger.info(event_data)

    def log_event(self, event_type_id, patch_grid_coord, active_tool_id=None,
                  **kwargs):

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

        if active_tool_id is None:
            active_tool_id = self._active_tool

        elif active_tool_id == "?":
            active_tool_id = self._active_tool
        else:
            self.active_tool = active_tool_id

        event_data = {}
        event_data['event_type_id'] = event_type_id
        event_data['timestamp'] = st
        event_data['patch_grid_coordinate'] = patch_grid_coord
        event_data['active_tool_id'] = active_tool_id

        for key, value in kwargs.items():
            event_data[key] = value

        self._event_logger.info(event_data)
