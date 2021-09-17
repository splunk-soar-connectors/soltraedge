# File: taxii_parser.py
# Copyright (c) 2014-2021 Splunk Inc.
#
# SPLUNK CONFIDENTIAL - Use or disclosure of this material in whole or in part
# without a valid written license from Splunk Inc. is PROHIBITED.

import sys
import io
import simplejson as json
import libtaxii as lt
import stix_parser as sp


def parse_taxii_message(taxii_message, base_connector=None):

    number_of_cbs = len(taxii_message.content_blocks)

    if not number_of_cbs:
        return {'error': 'no control blocks found'}

    packages = []

    for i, cb in enumerate(taxii_message.content_blocks):

        if base_connector:
            base_connector.send_progress("Parsing Content Block # {0}".format(i))

        # Give it to the stix parser to create the containers and artifacts
        # This code is the only place where the stix parsing will be written
        stix_xml = cb.content
        cstrio = io.BytesIO()
        cstrio.write(stix_xml)
        cstrio.seek(0)

        package = sp.parse_stix(cstrio, base_connector)

        if package:
            # print (json.dumps(package, indent=' ' * 4))
            packages.append(package)

    return sp.parse_packages(packages, base_connector)


if __name__ == '__main__':

    import pudb
    pudb.set_trace()

    results = None
    with open(sys.argv[1]) as f:

        # first try to parse it as a taxii message
        try:
            taxii_msg = lt.tm11.get_message_from_xml(f.read())
        except:
            # Now as a a stix document
            try:
                f.seek(0)
                package = sp.parse_stix(f, None)
                if package:
                    packages = [package]
                    results = sp.parse_packages(packages, None)
            except:
                raise
        else:
            results = parse_taxii_message(taxii_msg, None)

        # import pprint;pprint.pprint(results)
        with open('./taxii-parsed.json', 'w') as f:
            f.write(json.dumps(results, indent=' ' * 4))
