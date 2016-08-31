#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import
from exception import AVRException
from avr import YamahaAPI
import traceback

api = YamahaAPI(ctrl_url=open("receiver_url.txt", "r").read())
api.load_api_dictionary('Yamaha_AVR_API.def')
api.enable_request_validation()
api.print_available_commands()
print()

#for cmd in [x[:-4] for x in api.get_available_commands() if ".GET" in x]:
#    try:
#        res = api.create_command(cmd).get()
#        print("Result:\n{res}\n".format(res=str(res)))
#    except AVRException as e:
#        print("{err}".format(err=e))

print("Power: {power}".format(power=api.Main_Zone.Power_Control.Power.get()))
api.Main_Zone.Power_Control.Power = "On"

api.Main_Zone.Volume.Lvl = { "Val": "Up 1 dB", "Exp":"", "Unit":"" }
api.create_command("Main_Zone.Volume.Lvl").put(Val="Down 1 dB", Exp="", Unit="")

def call_except(fun):
    try:
        fun()
    except AVRException:
        traceback.print_exc()

#call_except(lambda: api.main_zone.power_control.power.put("On-"))
#call_except(lambda: api.main_zone.power_controller.get())
