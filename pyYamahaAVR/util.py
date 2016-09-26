#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import version_info
from .exception import ConfigException
import xml.etree.ElementTree as ET
import logging


class LogMixin(object):
    @property
    def logger(self):
        return logging.getLogger(self.__class__.__name__)


def init_logging():
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.basicConfig(level=logging.WARNING, format='%(levelname)8s: %(name)s: %(message)s')


def py_version():
    return version_info.major, version_info.minor


def format_params(param_list):
    if isinstance(param_list, list):
        return "[{}]".format(", ".join(map(lambda x: '"%s"' % x, param_list)))
    elif isinstance(param_list, dict):
        return "{{{}}}".format(gather_params(param_list))
    else:
        return param_list


def gather_params(d):
    params = []
    for (key, val) in d.items():
        params.append("{key}={params}".format(key=key, params=format_params(val)))
    return ", ".join(sorted(params))


def flatten_command_dict(d):
    items = []
    for (key, val) in d.items():
        if isinstance(val, dict):
            if key == 'PUT':
                item = "{key} = {{{params}}}".format(key=key, params=gather_params(val))
                items.append(item)
            else:
                items += ["{key}.{sub_cmd}".format(key=key, sub_cmd=sub_cmd) for sub_cmd in flatten_command_dict(val)]
        elif isinstance(val, bool):
            if val:
                items.append(key)
        elif isinstance(val, list):
            item = "{key} = {params}".format(key=key, params=format_params(val))
            items.append(item)
        elif val == str:
            item = "{key} = {params}".format(key=key, params='str')
            items.append(item)
        else:
            raise ConfigException("Ill-formed config entry: {key}={val}".format(key=key, val=val))
    return items


try:
    basestring  # attempt to evaluate basestring
    def isstr(s):
        return isinstance(s, basestring)
except NameError:
    def isstr(s):
        return isinstance(s, str)


# monkey patching ET because of self-closing elements
if py_version() < (3, 4):
    if py_version() < (3, 0):
        # py 2.x
        def _serialize_xml_without_self_closed_elements(write, elem, encoding, qnames, namespaces):
            """
            Function used to monkey patch ElementTrees serialize function that does
            not self close empty elements with python v2
            """
            tag = elem.tag
            text = elem.text
            if tag is ET.Comment:
                write("<!--%s-->" % ET._encode(text, encoding))
            elif tag is ET.ProcessingInstruction:
                write("<?%s?>" % ET._encode(text, encoding))
            else:
                tag = qnames[tag]
                if tag is None:
                    if text:
                        write(ET._escape_cdata(text, encoding))
                    for e in elem:
                        _serialize_xml_without_self_closed_elements(write, e, encoding, qnames, None)
                else:
                    write("<" + tag)
                    items = elem.items()
                    if items or namespaces:
                        if namespaces:
                            for v, k in sorted(namespaces.items(),
                                               key=lambda x: x[1]):  # sort on prefix
                                if k:
                                    k = ":" + k
                                write(" xmlns%s=\"%s\"" % (
                                    k.encode(encoding),
                                    ET._escape_attrib(v, encoding)
                                    ))
                        for k, v in sorted(items):  # lexical order
                            if isinstance(k, ET.QName):
                                k = k.text
                            if isinstance(v, ET.QName):
                                v = qnames[v.text]
                            else:
                                v = ET._escape_attrib(v, encoding)
                            write(" %s=\"%s\"" % (qnames[k], v))

                    write(">")
                    if text:
                        write(ET._escape_cdata(text, encoding))
                    for e in elem:
                        _serialize_xml_without_self_closed_elements(write, e, encoding, qnames, None)
                    write("</" + tag + ">")

            if elem.tail:
                write(ET._escape_cdata(elem.tail, encoding))

        # monkey patch the serialize method to stop emitting self closed elements,
        # Yamaha AVR doesn't like them. Can't use ET.tostring(xml_payload, method='html') either
        # because some HTML elements like '<input>' aren't closed...
        ET._serialize_xml = _serialize_xml_without_self_closed_elements
    else:
        # py 3.0 - 3.3
        def _serialize_xml_without_self_closed_elements(write, elem, qnames, namespaces):
            """
            Function used to monkey patch ElementTrees serialize function that does
            not self close empty elements with python v2
            """
            tag = elem.tag
            text = elem.text
            if tag is ET.Comment:
                write("<!--%s-->" % text)
            elif tag is ET.ProcessingInstruction:
                write("<?%s?>" % text)
            else:
                tag = qnames[tag]
                if tag is None:
                    if text:
                        write(ET._escape_cdata(text))
                    for e in elem:
                        _serialize_xml_without_self_closed_elements(write, e, qnames, None)
                else:
                    write("<" + tag)
                    items = list(elem.items())
                    if items or namespaces:
                        if namespaces:
                            for v, k in sorted(namespaces.items(),
                                               key=lambda x: x[1]):  # sort on prefix
                                if k:
                                    k = ":" + k
                                write(" xmlns%s=\"%s\"" % (
                                    k,
                                    ET._escape_attrib(v)
                                ))
                        for k, v in sorted(items):  # lexical order
                            if isinstance(k, ET.QName):
                                k = k.text
                            if isinstance(v, ET.QName):
                                v = qnames[v.text]
                            else:
                                v = ET._escape_attrib(v)
                            write(" %s=\"%s\"" % (qnames[k], v))

                    write(">")
                    if text:
                        write(ET._escape_cdata(text))
                    for e in elem:
                        _serialize_xml_without_self_closed_elements(write, e, qnames, None)
                    write("</" + tag + ">")

            if elem.tail:
                write(ET._escape_cdata(elem.tail))

        # monkey patch the serialize method to stop emitting self closed elements,
        # Yamaha AVR doesn't like them. Can't use ET.tostring(xml_payload, method='html') either
        # because some HTML elements like '<input>' aren't closed...
        ET._serialize['xml'] = _serialize_xml_without_self_closed_elements


def serialize_xml(xml_root):
    if py_version() >= (3, 4):
        return ET.tostring(xml_root, method='xml', encoding="utf-8", short_empty_elements=False)
    else:
        return ET.tostring(xml_root, method='xml', encoding="utf-8")