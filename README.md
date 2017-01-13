# ip_range_separator

SUMMARY
This is a script that takes a file with IP ranges that are dash-separated (e.g. 192.168.1.1-192.168.1.255) 
or in CIDR notation (e.g. 192.168.1.0/24) and outputs a list with a single IP per line that can be used by 
NMAP.  The input file can have comma separated IP ranges, individual IPs, but the script assumes that all 
IPs are real and correctly typed.  There is no input validation for IPs with octets that are too high 
(257 and up) or IPs containing more than 4 octets.

SYNTAX
"ip_range_separator.py [filename]" selects file to read.
--help displays brief help

IMPORTS
This script depends on the "sys" import 

