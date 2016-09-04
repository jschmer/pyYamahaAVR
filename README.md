# pyYamahaAVR

Generic python API to control your Yamaha AVR over the network.

## Basics
The API does not provide predefined commands/methods but provides a dynamic way to generate a command on the fly. Responses from the receiver will be mapped to a result object that provides the result as attributes. See [Usage](#usage) section to see this in action.

Search for [Yamaha RX Function Tree] to find an Excel workbook that defines all the commands that may be supported. Note that your device may not support all available commands. Or see the section [Optional command definition file](#optional-command-definition-file) to get a subset of commands available.

## Usage
```
>>> from avr import YamahaAPI
>>> api = YamahaAPI("http://<AVR_IP>/YamahaRemoteControl/ctrl")
>>>
>>> # Get power status
>>> api.Main_Zone.Power_Control.Power.get()
'Standby'
>>>
>>> # Set power status
>>> api.Main_Zone.Power_Control.Power.put("Standby")
>>> api.Main_Zone.Power_Control.Power = "On"
>>>
>>> # Set volume with multiple parameters
>>> api.Main_Zone.Volume.Lvl = { "Val": "Up 1 dB", "Exp":"", "Unit":"" }
>>>
>>> # Get volume and print result
>>> res = api.Main_Zone.Volume.Lvl.get()
>>> res
<pyYamahaAVR.avr.result_struct instance at 0x0000000003B086C8>
>>> print(res)
Exp=1
Unit=dB
Val=-410
>>> res.Val
'-405'
>>>
>>> # Another way to create commands
>>> cmd = api.create_command("Main_Zone.Volume.Lvl")
>>> print(cmd.get())
Exp=1
Unit=dB
Val=-400
>>> cmd.put({ "Val": "Up 1 dB", "Exp":"", "Unit":"" })
```

## Optional command definition file
You can also use and load a command definition file (see 'Yamaha_AVR_API.def') to be able to get a list of commands that are supported. This definition file is currenlty not complete and does not have all commands that your device supports. Pull requests for additional commands are welcome!
After loading the file you can print all available commands to get an overview of what is supported. You can also enable request validation to help spotting errors when trying to change values on the device. Trying to send an invalid command will then generate an exception.

```
>>> api.load_api_dictionary()
>>> api.print_available_commands()
Main_Zone.Power_Control.Sleep.PUT = ["Off", "30 min", "60 min", "90 min", "120 min", "Last"]
Main_Zone.Power_Control.Sleep.GET
Main_Zone.Power_Control.Power.PUT = ["Standby", "On", "On/Standby"]
Main_Zone.Power_Control.Power.GET
Main_Zone.Volume.Lvl.PUT = {Exp=[""], Unit=[""], Val=["Down", "Up", "Down 1 dB", "Up 1 dB", "Down 2 dB", "Up 2 dB", "Down 5 dB", "Up 5 dB"]}
Main_Zone.Volume.Lvl.GET
Main_Zone.Volume.Mute.PUT = ["On/Off"]
Main_Zone.Volume.Mute.GET
...
>>>
>>> # Or use your own definition file
>>> api.load_api_dictionary('My_Yamaha_AVR_API.def')
>>>
>>> api.enable_request_validation()
>>> api.Main_Zone.Volume.Lvl = { "Val": "Up 1 dB", "Exp":"", "Unit":"" }
>>>
>>> api.Main_Zone.Volume.Lvl = { "Val": "Up 1 dB", "Exp":"", "Unit":"x" }
exception.ValueNotSupportedException: Unsupported value 'x' (valid options: [u'']) for parameter 'Unit'
>>>
>>> api.Main_Zone.VolumeLvl = { "Val": "Up 1 dB", "Exp":"", "Unit":"" }
exception.CommandNotAvailableException: Command not available: 'Main_Zone.VolumeLvl'
>>>
>>> api.Main_Zone.Volume.Lvl = { "Val": "Up 1 dB", "Exp":"" }
exception.ParameterMissingException: Missing parameter 'Unit'
```


## License

The MIT License (MIT)

Copyright (c) 2016 jschmer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

[Yamaha RX Function Tree]: https://www.google.de/search?q=Yamaha+RX+Function+Tree
