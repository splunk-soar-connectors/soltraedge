# --
# File: soltraedge_consts.py
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

SOLTRAEDGE_JSON_USE_SSL = "use_ssl"
SOLTRAEDGE_JSON_COLLECTION = "collection"
SOLTRAEDGE_JSON_DEF_NUM_DAYS = "interval_days"
SOLTRAEDGE_CONNECTED_TO_SERVER = "Connected to server"
SOLTRAEDGE_VALIDATING_FEED = "Validating collection"

SOLTRAEDGE_ERR_COLLECTION_NOT_FOUND = "Collection '{collection}' not found"
SOLTRAEDGE_ERR_CONNECTING_TO_SERVER = "Error connecting to server"
SOLTRAEDGE_SUCC_CONNECTIVITY_TEST = "Connectivity test passed"
SOLTRAEDGE_ERR_CONNECTIVITY_TEST = "Connectivity test failed"
SOLTRAEDGE_ERR_END_TIME_LT_START_TIME = "End time less than start time"
SOLTRAEDGE_ERR_HTTP_ERROR = "HTTP Connection error with code '{code}', reason '{reason}'"
SOLTRAEDGE_ERR_TRY_SSL_CONFIG_CHANGE = "\nPlease try again after changing the SSL config on the asset"
SOLTRAEDGE_ERR_UNABLE_TO_PARSE_TAXII_MSG = "Unable to parse the received taxii message"

SOLTRAEDGE_MSG_COLLECTION_LIST = "Please configure one of the following collections found on the Edge box:"
SOLTRAEDGE_MSG_COLLECTION_LIST += "\n--------------\n{collections}\n-----------\n"
SOLTRAEDGE_POLLING_SERVER_INDICATOR = "Polling server for data between {start_ts} and {end_ts}"
SOLTRAEDGE_PARSING_DATA_FROM_SERVER = "Parsing data from server"
SOLTRAEDGE_GOT_CB = "Got {len_cb} TAXII content blocks"
SOLTRAEDGE_PARSING_NTH_CB = "Control Block # {i}"

SOLTRAEDGE_MILLISECONDS_IN_A_DAY = 86400000
SOLTRAEDGE_NUMBER_OF_DAYS_BEFORE_ENDTIME = 1

# Ingestion labels to use
CONTAINER_LABEL = "Incident"
ARTIFACT_LABEL = "Event"
SOLTRAEDGE_DEFAULT_CONTAINER_COUNT = 10
SOLTRAEDGE_DEFAULT_ARTIFACT_COUNT = 100
