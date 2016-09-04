#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division, unicode_literals, absolute_import
import os
import requests
import xml.etree.ElementTree as ET
from .exception import *
from . import util


class Command(object):
    """
    Utility class to help building and calling commands for your API with a nice
    syntax. Your API object will serve as a factory for commands, see YamahaAPI
    documentation for more details.
    Chaining attributes will create nested commands.
    Forwards actual network requests to the API object. See YamahaAPI documentation
    for details on network requests.

    Example:
        # GET command:
        cmd.get()

        # PUT command, single parameter:
        cmd.put('Off')
        cmd = 'OFF'

        # PUT command, multiple parameter:
        cmd.put(Val='Up', Unit='', Exp='')
        cmd = {
            'Val': 'Up',
            'Unit': '',
            'Exp': ''
        }

        # Nested command:
        api.System.Power_Control.Power.get()
    """
    def __init__(self, api_obj, cmd_list):
        self.api_obj = api_obj
        if isinstance(cmd_list, list):
            self.cmd_list = cmd_list
        else:
            self.cmd_list = cmd_list.split(".")

    def __getattr__(self, item):
        """"""
        return Command(self.api_obj, self.cmd_list + [item])

    def __setattr__(self, name, value):
        if name in ["cmd_list", "api_obj"]:
            super(Command, self).__setattr__(name, value)
        else:
            getattr(self, name).put(value)

    def __unicode__(self):
        return u'''<{cls} '{cmd}' at {addr}>'''.format(
            cls=self.__class__.__name__,
            cmd=self.command_str(),
            addr=hex(id(self))
        )

    def __repr__(self):
        return self.__unicode__()

    def __str__(self):
        return self.__unicode__()

    def command_str(self):
        return ".".join(self.cmd_list)

    def get(self):
        """
        Actually perform the GET command. Will raise exceptions when anything goes
        wrong.
        """
        return self.api_obj._get(self)

    def put(self, param=None, **kwargs):
        """
        Actually perform the PUT command. Will raise exceptions when anything goes
        wrong.
        """
        return self.api_obj._put(self, param, **kwargs)


class YamahaAPI(util.LogMixin):
    """
    Main class to interact with your Yamaha AVR.

    Query available commands with `get_available_commands()`. This needs an api dictionary loaded
    with `load_api_dictionary(file)`.

    Create commands easily with attribute driven commands or with create_command(command_text).
    Note: commands are case sensitive!

    Examples:
        # Query power status
        api.System.Power_Control.Power.get()
            or
        api.create_command("System.Power_Control.Power").get()

        # Set power status
        api.System.Power_Control.Power.put("On")
            or
        api.System.Power_Control.Power = "On"

    See `Command` documentation for more details regarding commands.
    """
    def __init__(self, ctrl_url):
        self.ctrl_url = ctrl_url
        self.api_dict = None
        self.validate_requests = False

    def load_api_dictionary(self, file=None):
        """
        Load api dictionary that contains available commands.
        Used to create available command list and also needed for
        request validation.
        """
        if not file:
            # API.def should be installed alongside this file
            file = os.path.join(
                os.path.dirname(__file__),
                'Yamaha_AVR_API.def'
            )

        if hasattr(file, 'read'):
            self.api_dict = eval(file.read())
        else:
            self.api_dict = eval(open(file, 'r').read())

    def enable_request_validation(self, status=True):
        """
        Enables request validation with provided api dictionary.
        Requests will raise Exceptions when the request is ill-formed
        according to provided api dictionary.
        """
        if status and not self.api_dict:
            raise ConfigException("Request validation needs an API dictionary loaded! See func 'load_api_dictionary'")
        self.validate_requests = status

    def get_available_commands(self):
        return util.flatten_command_dict(self.api_dict)

    def print_available_commands(self):
        print("\n".join(self.get_available_commands()))

    def __getattr__(self, item):
        return Command(self, [item])

    def create_command(self, cmd):
        return Command(self, cmd)

    def _is_command_available(self, cmd_list):
        if not self.validate_requests:
            return True

        try:
            dict_iter = self.api_dict
            for cmd in cmd_list:
                dict_iter = dict_iter[cmd]
            return True
        except KeyError:
            return False

    def _get_command_config(self, mode, cmd_list):
        dict_iter = self.api_dict
        for cmd in cmd_list:
            dict_iter = dict_iter[cmd]
        return dict_iter[mode]

    def _check_get_command(self, cmd_builder):
        if not self.validate_requests:
            return True

        if not self._is_command_available(cmd_builder.cmd_list):
            raise CommandNotAvailableException("Command not available: '{cmd}'".format(cmd=cmd_builder.command_str()))

        try:
            return self._get_command_config('GET', cmd_builder.cmd_list)
        except KeyError:
            return False

    def _check_params(self, specified_params, valid_params):
        for key, val in valid_params.items():
            if key not in specified_params:
                # param not specified
                raise ParameterMissingException(
                   "Missing parameter '{missing_param}'"
                   .format(missing_param=key)
                )
            elif isinstance(val, dict):
                if not isinstance(specified_params[key], dict):
                    raise ValueNotSupportedException(
                        "Unsupported value '{value}' (valid options: {valid_options}) for parameter '{param}'"
                        .format(value=specified_params[key], valid_options=val, param=key)
                    )
                else:
                    # check that all subparams are there
                    self._check_params(specified_params[key], val)
            elif isinstance(val, list):
                if specified_params[key] not in val:
                    raise ValueNotSupportedException(
                        "Unsupported value '{value}' (valid options: {valid_options}) for parameter '{param}'"
                        .format(value=specified_params[key], valid_options=val, param=key)
                    )
                else:
                    pass
            else:
                if not util.isstr(specified_params[key]):
                    raise ValueNotSupportedException(
                        "Unsupported value '{value}' (valid options: {valid_options}) for parameter '{param}'"
                        .format(value=specified_params[key], valid_options=val, param=key)
                    )
                else:
                    pass

    def _check_put_command(self, cmd_builder, args):
        if not self.validate_requests:
            return True

        if not self._is_command_available(cmd_builder.cmd_list):
            raise CommandNotAvailableException("Command not available: '{cmd}'".format(cmd=cmd_builder.command_str()))

        cmd_list = cmd_builder.cmd_list
        try:
            options = self._get_command_config('PUT', cmd_list)
            if isinstance(options, dict) and isinstance(args, dict):
                self._check_params(args, options)
            elif isinstance(options, list) and args not in options:
                raise ValueNotSupportedException(
                    "Unsupported value '{value}' (valid options: {valid_options})"
                    .format(value=args, valid_options=options)
                )
            elif not util.isstr(args):
                raise ValueNotSupportedException(
                    "Unsupported value '{value}' (valid options: {valid_options})"
                    .format(value=args, valid_options=options)
                )
            else:
                pass
        except KeyError:
            return False

    def _request(self, xml_payload):
        # We are using a monkey-patched xml serialization method to stop emitting self-closed
        # elements because the Yamaha AVR doesn't like them, see func _serialize_xml_without_self_closed_elements
        payload_str = util.serialize_xml(xml_payload).decode('utf-8')
        self.logger.debug("Request: {payload}".format(payload=payload_str))

        res = requests.post(
            self.ctrl_url,
            data=payload_str,
            headers={"Content-Type": "text/xml"}
        )
        if res.status_code != 200:
            raise RequestException("Status Code: {err}, request: '{request}'".format(request=payload_str, err=res.status_code))

        try:
            response = ET.XML(res.content)
            if response.get("RC") != "0":
                raise ResponseException("Command failed, reponse: '{response}'".format(response=res.content))
        except ET.ParseError as e:
            raise ResponseException("Invalid response: '{response}', Error: {err}".format(response=res.content, err=e))

        self.logger.debug("Response: {response}".format(response=util.serialize_xml(response).decode('utf-8')))
        return response

    def _request_get(self, cmd_list):
        request_xml = ET.Element('YAMAHA_AV')
        request_xml.set('cmd', 'GET')

        sub_ele = request_xml
        for cmd in cmd_list:
            sub_ele = ET.SubElement(sub_ele, cmd)
        sub_ele.text = 'GetParam'

        res = self._request(request_xml)

        # Parse response values, this will be either a single text value or an object with
        # respective attributes
        search_path = "/".join(cmd_list)
        parsed_result = res.find(search_path).text
        if parsed_result:
            return parsed_result

        class result_struct:
            def __init__(self, attrs):
                for attr, value in attrs.items():
                    setattr(self, attr, value)

            def _get_attrs(self):
                attrs = []
                for attr, value in self.__dict__.items():
                    if attr.startswith("__"):
                        continue

                    if isinstance(value, type(self)):
                        for subattr_str in value._get_attrs():
                            attrs.append("{attr_name}.{subattr_str}".format(attr_name=attr,
                                                                            subattr_str=subattr_str))
                    else:
                        attrs.append("{attr_name}={attr_value}".format(attr_name=attr, attr_value=value))
                return sorted(attrs)

            def __str__(self):
                return "\n".join(self._get_attrs())

        def get_parsed_value(obj):
            if obj.text:
                return obj.text
            else:
                # got subelements, add them as a property
                attrs = {}
                for sub in obj:
                    attrs[sub.tag] = get_parsed_value(sub)
                return result_struct(attrs)

        result_dummy = result_struct({})
        for ele in res.find(search_path):
            setattr(result_dummy, ele.tag, get_parsed_value(ele))

        return result_dummy

    def _add_param_dict_to_request_xml(self, parent_ele, params):
        for param, value in params.items():
            param_ele = ET.SubElement(parent_ele, param)
            if isinstance(value, dict):
                self._add_param_dict_to_request_xml(param_ele, value)
            else:
                param_ele.text = value

    def _request_put(self, cmd_list, params):
        request_xml = ET.Element('YAMAHA_AV')
        request_xml.set('cmd', 'PUT')

        sub_ele = request_xml
        for cmd in cmd_list:
            sub_ele = ET.SubElement(sub_ele, cmd)

        if isinstance(params, dict):
            # got multiple values, add them as a subelement
            self._add_param_dict_to_request_xml(sub_ele, params)
        else:
            sub_ele.text = params

        res = self._request(request_xml)

    def _get(self, cmd_builder):
        self._check_get_command(cmd_builder)
        self.logger.info("GET: '{cmd}'".format(cmd=cmd_builder.command_str()))
        return self._request_get(cmd_builder.cmd_list)

    def _put(self, cmd_builder, param=None, **kwargs):
        """"
        Sends a PUT command. Either param or kwargs is set.
        The former is a PUT command with single parameter.
        The latter is a PUT command with multiple parameters.
        """
        used_param = param or kwargs
        self._check_put_command(cmd_builder, used_param)
        self.logger.info("""PUT: '{cmd}' = '{param}'""".format(cmd=cmd_builder.command_str(), param=used_param))
        self._request_put(cmd_builder.cmd_list, used_param)
