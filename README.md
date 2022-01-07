[comment]: # "Auto-generated SOAR connector documentation"
# Soltra Edge

Publisher: Phantom  
Connector Version: 1\.2\.28  
Product Vendor: Soltra  
Product Name: Edge  
Product Version Supported (regex): "\.\*"  
Minimum Product Version: 1\.2\.236  

This App acts as a STIX client and implements the ingest action to pull data from a Soltra Edge device to create containers and artifacts\.

[comment]: # "File: readme.md"
[comment]: # "Copyright (c) 2014-2016 Splunk Inc."
[comment]: # ""
[comment]: # "Licensed under the Apache License, Version 2.0 (the 'License');"
[comment]: # "you may not use this file except in compliance with the License."
[comment]: # "You may obtain a copy of the License at"
[comment]: # ""
[comment]: # "    http://www.apache.org/licenses/LICENSE-2.0"
[comment]: # ""
[comment]: # "Unless required by applicable law or agreed to in writing, software distributed under"
[comment]: # "the License is distributed on an 'AS IS' BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,"
[comment]: # "either express or implied. See the License for the specific language governing permissions"
[comment]: # "and limitations under the License."
[comment]: # ""
This App is an Ingestion source. In the Phantom documentation, in the [Administration
Manual](../admin/) under the [Data Sources](../admin/sources) section, you will find an explanation
of how Ingest Apps works and how information is extracted from the ingested data. There is a general
explanation in Overview, and some individuals Apps have their own sections.


### Configuration Variables
The below configuration variables are required for this Connector to operate.  These variables are specified when configuring a Edge asset in SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**device** |  required  | string | Server IP/Hostname
**use\_ssl** |  required  | boolean | Use SSL
**username** |  required  | string | Username
**password** |  required  | password | Password
**collection** |  required  | string | Collection \(Feed\) name used for ingestion

### Supported Actions  
[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity\. This action validates the feed name on Soltra Edge to check the connection and credentials\.  
[on poll](#action-on-poll) - Callback action for the on\_poll ingest functionality\.  

## action: 'test connectivity'
Validate the asset configuration for connectivity\. This action validates the feed name on Soltra Edge to check the connection and credentials\.

Type: **test**  
Read only: **True**

#### Action Parameters
No parameters are required for this action

#### Action Output
No Output  

## action: 'on poll'
Callback action for the on\_poll ingest functionality\.

Type: **ingest**  
Read only: **True**

#### Action Parameters
PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**start\_time** |  optional  | Start of time range, in epoch time \(milliseconds\) | numeric | 
**end\_time** |  optional  | End of time range, in epoch time \(milliseconds\) | numeric | 
**container\_count** |  optional  | Maximum number of container records to query for\. | numeric | 
**artifact\_count** |  optional  | Maximum number of artifact records to query for\. | numeric | 

#### Action Output
No Output