# --
# File: soltraedge_connector.py
#
# Copyright (c) Phantom Cyber Corporation, 2014-2018
#
# This unpublished material is proprietary to Phantom Cyber.
# All rights reserved. The methods and
# techniques described herein are considered trade secrets
# and/or confidential. Reproduction or distribution, in whole
# or in part, is forbidden except by express written permission
# of Phantom Cyber.
#
# --

# Phantom imports
import phantom.app as phantom
from phantom.app import BaseConnector
# from phantom.app import ActionResult

# THIS Connector imports
from soltraedge_consts import *
import taxii_parser

from datetime import datetime
from datetime import timedelta
import time
import libtaxii as lt
import libtaxii.clients as tc
import libtaxii.messages_11 as tm11
from libtaxii.constants import *
import urllib2
# from collections import defaultdict
import simplejson as json

_container_common = {
    "description": "Container added by Phantom",
    "run_automation": False  # Don't run any playbooks, when this container is added
}

_artifact_common = {
    "type": "network",
    "description": "Artifact added by Phantom",
    "run_automation": False  # Don't run any playbooks, when this artifact is added
}


class SoltraedgeConnector(BaseConnector):

    def __init__(self):

        # Call the BaseConnectors init first
        super(SoltraedgeConnector, self).__init__()

        self._client = None

    def _create_client(self, param):

        config = self.get_config()

        username = config[phantom.APP_JSON_USERNAME]
        password = config[phantom.APP_JSON_PASSWORD]
        use_ssl = config[SOLTRAEDGE_JSON_USE_SSL]

        # set the parameters of the client
        client = tc.HttpClient()
        client.set_auth_type(tc.HttpClient.AUTH_BASIC)
        client.set_use_https(use_ssl)
        client.set_auth_credentials({'username': username, 'password': password})

        # Save this object
        self._client = client

        return phantom.APP_SUCCESS

    def _get_str_from_epoch(self, epoch_milli):
        # 2015-07-21T00:27:59Z
        return datetime.fromtimestamp(epoch_milli / 1000.0).strftime('%Y-%m-%dT%H:%M:%SZ')

    def _add_observable(self, observable, container_artifacts, data):

        # if any artifacts are present add them
        if ('artifacts' in observable):
            container_artifacts.extend(observable['artifacts'])

        # if any observable of this observable
        if ('observables' not in observable):
            return

        for child_observable in observable['observables']:
            if (child_observable not in data):
                continue

            self._add_observable(data[child_observable], container_artifacts, data)

        return phantom.APP_SUCCESS

    def _save_results(self, results, param):

        artifact_count = int(param.get(phantom.APP_JSON_ARTIFACT_COUNT, SOLTRAEDGE_DEFAULT_ARTIFACT_COUNT))
        container_count = int(param.get(phantom.APP_JSON_CONTAINER_COUNT, SOLTRAEDGE_DEFAULT_CONTAINER_COUNT))

        containers_processed = 0

        self.save_progress("Saving Containers and Artifacts")

        for i, result in enumerate(results):

            # container is a dictionary of a single container and artifacts
            if ('container' not in result):
                continue

            # container is a dictionary of a single container and artifacts
            if ('artifacts' not in result):
                # igonore containers without artifacts
                continue

            if (len(result['artifacts']) == 0):
                # igonore containers without artifacts
                continue

            containers_processed += 1

            # container = result['container']
            # if ('data' in container):
            #     del container['data']

            ret_val, response, container_id = self.save_container(result['container'])
            self.debug_print("save_container returns, value: {0}, reason: {1}".format(ret_val, response))

            if (phantom.is_fail(ret_val)):
                continue

            if (not container_id):
                continue

            # set the size of the artifacts to max configured for this ingestion
            artifacts = result['artifacts']
            artifacts = artifacts[:artifact_count]

            # get the length of the artifact, we might have trimmed it or not
            len_artifacts = len(artifacts)

            for j, artifact in enumerate(artifacts):

                if ('source_data_identifier' not in artifact):
                    artifact['source_data_identifier'] = j

                self.send_progress("Saving Container # {0}, Artifact # {1}".format(i + 1, j + 1))
                artifact['container_id'] = container_id
                artifact.update(_artifact_common)

                if ((j + 1) == len_artifacts):
                    artifact['run_automation'] = True

                ret_val, status_string, artifact_id = self.save_artifact(artifact)
                self.debug_print("save_artifact returns, value: {0}, reason: {1}, artifact_id: {2}".format(ret_val, status_string, artifact_id))

            if (containers_processed >= container_count):
                break

        self.send_progress(" ")
        return containers_processed

    def _get_start_end_time(self, param):

        if (self.is_poll_now()):
            # get data from app_config
            end_time = int(time.mktime(datetime.utcnow().timetuple())) * 1000
            num_days = int(self.get_app_config().get(SOLTRAEDGE_JSON_DEF_NUM_DAYS))
            start_time = end_time - (SOLTRAEDGE_MILLISECONDS_IN_A_DAY * num_days)
        else:
            start_time = param.get(phantom.APP_JSON_START_TIME)
            end_time = param.get(phantom.APP_JSON_END_TIME)
            curr_epoch_msecs = int(time.mktime(datetime.utcnow().timetuple())) * 1000
            end_time = curr_epoch_msecs if end_time is None else int(end_time)
            num_days = int(self.get_app_config().get(SOLTRAEDGE_JSON_DEF_NUM_DAYS, SOLTRAEDGE_NUMBER_OF_DAYS_BEFORE_ENDTIME))
            start_time = end_time - (SOLTRAEDGE_MILLISECONDS_IN_A_DAY * num_days) if start_time is None else int(start_time)

        self.debug_print("start_time: {0} end_time: {1}".format(start_time, end_time))

        # validate the time
        if (end_time < start_time):
            return (phantom.APP_ERROR, SOLTRAEDGE_ERR_END_TIME_LT_START_TIME, None, None)

        start_ts = self._get_str_from_epoch(start_time)
        end_ts = self._get_str_from_epoch(end_time)

        return (phantom.APP_SUCCESS, "", start_ts, end_ts)

    def _on_poll(self, param):

        # Connect to the server
        if (phantom.is_fail(self._create_client(param))):
            return self.get_status()

        (ret_val, ret_msg, start_ts, end_ts) = self._get_start_end_time(param)

        if (phantom.is_fail(ret_val)):
            return self.set_status(ret_val, ret_msg)

        config = self.get_config()

        collection_name = config[SOLTRAEDGE_JSON_COLLECTION]

        create_kwargs = {'message_id': tm11.generate_message_id(),
                'collection_name': collection_name,
                'exclusive_begin_timestamp_label': start_ts,
                'inclusive_end_timestamp_label': end_ts,
                'poll_parameters': tm11.PollRequest.PollParameters()}

        poll_req = tm11.PollRequest(**create_kwargs)
        poll_xml = poll_req.to_xml()

        self.save_progress(SOLTRAEDGE_POLLING_SERVER_INDICATOR, start_ts=start_ts, end_ts=end_ts)

        # Connect to the server
        device = config[phantom.APP_JSON_DEVICE]
        try:
            http_resp = self._client.call_taxii_service2(device, '/taxii-discovery-service/', VID_TAXII_XML_11, poll_xml)
        except Exception as e:
            return self.set_status(phantom.APP_ERROR, SOLTRAEDGE_ERR_CONNECTING_TO_SERVER, e)

        if (type(http_resp) == urllib2.HTTPError):
            # Looks like an error
            return self.set_status(phantom.APP_ERROR, SOLTRAEDGE_ERR_HTTP_ERROR, code=http_resp.code, reason=http_resp.reason)

        self.save_progress("Getting TAXII message..This may take some time")

        try:
            taxii_message = lt.get_message_from_http_response(http_resp, poll_req.message_id)
            self.debug_print("TAXII Message:", taxii_message.to_xml())
            # with open("./taxii.xml", "w") as f:
            #     f.write(taxii_message.to_xml())
        except Exception as e:
            return self.set_status(phantom.APP_ERROR, SOLTRAEDGE_ERR_UNABLE_TO_PARSE_TAXII_MSG, e)

        number_of_cbs = len(taxii_message.content_blocks)  # pylint: disable=E1101

        self.save_progress(SOLTRAEDGE_GOT_CB, len_cb=number_of_cbs)

        if (not number_of_cbs):
            return self.set_status(phantom.APP_SUCCESS)

        self.save_progress("Processing Control Blocks for relations")

        results = taxii_parser.parse_taxii_message(taxii_message, self)

        if ('error' in results):
            # Error
            return self.set_status(phantom.APP_ERROR, results['error'])

        self._save_results(results, param)

        return self.set_status(phantom.APP_SUCCESS)

    def _test_connectivity(self, param):

        # Connect to the server
        if (phantom.is_fail(self._create_client(param))):
            self.append_to_message(SOLTRAEDGE_ERR_CONNECTIVITY_TEST)
            return self.get_status()

        config = self.get_config()

        collection_name = config[SOLTRAEDGE_JSON_COLLECTION]
        device = config[phantom.APP_JSON_DEVICE]

        collection_request = tm11.CollectionInformationRequest(tm11.generate_message_id())
        collection_xml = collection_request.to_xml()

        # Connect to the server
        try:
            http_resp = self._client.call_taxii_service2(device, '/taxii-discovery-service/', VID_TAXII_XML_11, collection_xml)
        except Exception as e:
            self.set_status(phantom.APP_ERROR, SOLTRAEDGE_ERR_CONNECTING_TO_SERVER, e)
            self.append_to_message(SOLTRAEDGE_ERR_TRY_SSL_CONFIG_CHANGE)
            self.append_to_message(SOLTRAEDGE_ERR_CONNECTIVITY_TEST)
            return self.get_status()

        self.save_progress(SOLTRAEDGE_VALIDATING_FEED)

        if (type(http_resp) == urllib2.HTTPError):
            # Looks like an error
            self.set_status(phantom.APP_ERROR, SOLTRAEDGE_ERR_HTTP_ERROR, code=http_resp.code, reason=http_resp.reason)
            self.append_to_message(SOLTRAEDGE_ERR_CONNECTIVITY_TEST)
            return self.get_status()

        found = False
        try:
            taxii_message = lt.get_message_from_http_response(http_resp, collection_request.message_id)
            self.debug_print(taxii_message.to_xml())
        except Exception as e:
            self.set_status(phantom.APP_ERROR, SOLTRAEDGE_ERR_UNABLE_TO_PARSE_TAXII_MSG, e)
            self.append_to_message(SOLTRAEDGE_ERR_CONNECTIVITY_TEST)
            return self.get_status()

        collection_names = []

        # taxii_message is of type CollectionInformationResponse
        for collection_info in taxii_message.collection_informations:  # pylint: disable=E1101
            collection_names.append(collection_info.collection_name)
            if (collection_info.collection_name == collection_name):
                found = True
                break

        if (not found):
            self.save_progress(SOLTRAEDGE_ERR_COLLECTION_NOT_FOUND, collection=collection_name)
            self.save_progress(SOLTRAEDGE_MSG_COLLECTION_LIST, collections='\n'.join(collection_names))
            return self.set_status(phantom.APP_ERROR, SOLTRAEDGE_ERR_CONNECTIVITY_TEST)

        return self.set_status_save_progress(phantom.APP_SUCCESS, SOLTRAEDGE_SUCC_CONNECTIVITY_TEST)

    def handle_action(self, param):
        """Function that handles all the actions

        Args:

        Return:
            A status code
        """

        result = None
        action = self.get_action_identifier()

        if (action == phantom.ACTION_ID_INGEST_ON_POLL):
            start_time = time.time()
            result = self._on_poll(param)
            end_time = time.time()
            diff_time = end_time - start_time
            human_time = str(timedelta(seconds=int(diff_time)))
            self.save_progress("Time taken: {0}".format(human_time))
        elif (action == phantom.ACTION_ID_TEST_ASSET_CONNECTIVITY):
            result = self._test_connectivity(param)

        return result

if __name__ == '__main__':

    import sys
    # import simplejson as json
    import pudb
    pudb.set_trace()

    if (len(sys.argv) < 2):
        print "No test json specified as input"
        exit(0)

    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=' ' * 4))

        connector = SoltraedgeConnector()
        connector.print_progress_message = True
        ret_val = connector._handle_action(json.dumps(in_json), None)
        print ret_val

    exit(0)
