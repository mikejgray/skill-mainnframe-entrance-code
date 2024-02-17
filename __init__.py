# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import os
from ovos_bus_client.message import Message
from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler, skill_api_method


class BootFinishedSkill(OVOSSkill):
    def initialize(self):
        self.add_event("mycroft.ready", self.handle_ready)
        self.attempts = 0
        self.active_user = ""

    @property
    def entrance_codes(self):
        return self.settings.get("entrance_codes", {})

    @property
    def speak_ready(self):
        """
        Speak `ready` dialog when ready unless disabled in settings
        """
        return self.settings.get("speak_ready", True)

    @property
    def ready_sound(self):
        """
        play sound when ready unless disabled in settings
        """
        return self.settings.get("ready_sound", True)

    @skill_api_method
    def get_active_user(self):
        return self.active_user

    def handle_ready(self, message: Message):
        """
        Handle mycroft.ready event. Notify the user everything is ready if
        configured.
        """
        if self.ready_sound:
            self.acknowledge()
        self.enclosure.eyes_on()
        if self.speak_ready:
            self.speak_dialog("ready")
        else:
            self.log.debug("Ready notification disabled in settings")
        self.enclosure.eyes_blink("b")
        if not self.settings.get("entrance_codes"):
            self.log.warning(f"No entrance codes configured, please add them in the skill settings at {self.settings.path}")
        self.authenticate_user()

    @intent_handler("enable_ready_notification.intent")
    def handle_enable_notification(self, message: Message):
        """
        Handle a request to enable ready announcements
        """
        self.settings["speak_ready"] = True
        self.speak_dialog("confirm_speak_ready")

    @intent_handler("disable_ready_notification.intent")
    def handle_disable_notification(self, message: Message):
        """
        Handle a request to disable ready announcements
        """
        self.settings["speak_ready"] = False
        self.speak_dialog("confirm_no_speak_ready")

    def authenticate_user(self):
        user_code = self.get_response("entrance_code")

        if self.attempts == 3:
            self.speak_dialog("shutdown")
            self.bus.emit(Message("system.shutdown"))
            self.attempts = 0
            return
        for user, entrance_code in self.entrance_codes.items():
            if user_code == entrance_code:
                self.speak_dialog("valid_code", data={"user": user})
                self.active_user = user
                break
        if not self.active_user:
            self.speak_dialog("wrong_code", data={"code": user_code})
            self.attempts += 1
            self.authenticate_user()

        self.connect_to_spotify()

    def connect_to_spotify(self):
        connect_to_spotify = self.get_response("ask_spotify_connect")

        if connect_to_spotify == "yes":
            self.speak_dialog("spotify_connecting")
            os.system("spotify-up")
            self.speak_dialog("spotify_connected")
