#!/usr/bin/python

import sys
import string

#Reads multiline files with CIDR notation or dash-separated IP ranges
#and outputs one or more files with one IP address per line.  This script
#assumes that all IPs are within real ranges (e.g. not 192.168.257.23) 
#and that IP ranges are either line separated, comma separated, or both.



#Read environmental variables from command line, if there is a single file,
#returns a list with a single entry.  If there is an exclusion file, returns 
#a list with two entries.
def read_env_vars():
	file_names = []
	arg_list = str(sys.argv)
	if len(sys.argv)<2:
		print "Missing argument, you must inclide the file with IP ranges"
		sys.exit()
	if "--help" in sys.argv[1]:
		print 'This script takes a file with IP ranges that are dash "-" separated'
		print 'or in CIDR notation and expands them to one or more output files.  '
		print 'It assumes that there are no mistakes in the IP lists and that all '
		print 'IPs are real (e.g. not 192.168.2.285)'
		print "\nSyntax: ip_range_separator.py [IP list to separate]"
		sys.exit()
	if len(sys.argv)==2:
		ip_range_file = str(sys.argv[1])
		file_names.append(ip_range_file)
	if len(sys.argv)>2:
		ip_range_file = str(sys.argv[1])
		ip_exclusion_file = str(sys.argv[2])
		file_names.append(ip_range_file)
		file_names.append(ip_exclusion_file)
	return file_names

#Takes input file and returns a list of the ranges to calculate, with only
#two possible formats: CIDR notation and dash-separated.  Asks for verification
#if the format is unrecognized.
def parse_raw_input(filename):
	range_list = []
	file = open(filename, 'r')
	lines = file.readlines()
	for line in lines:
		if "," in line:
			tmp = line.split(",")
			for item in tmp:
				range_list.append(item)
		else:
			range_list.append(line)
	for x in range(0, len(range_list)):
		range_list[x] = range_list[x].strip()
	return range_list

#Takes string as input in format xxx.xxx.xxx.xxx-xxx.xxx.xxx.xxx and splits it
#into individual IPs
def range_splitter(ip_range):
	list = []
	
	#two integer lists [xxx,xxx,xxx,xxx]
	start = ip_range.split("-")[0].split(".")
	end = ip_range.split("-")[1].split(".")
	for x in range(0, 4):
		start[x] = int(start[x])
		end[x] = int(end[x])
	
	while start[0]<end[0] or start[1]<end[1] or start[2]<end[2] or start[3]<end[3]:
		list.append(str(start[0])+"."+str(start[1])+"."+str(start[2])+"."+str(start[3]))
		start[3]+=1
		if start[3]>255:
			start[3]=0
			start[2]+=1
		if start[2]>255:
			start[2]=0
			start[1]+=1
		if start[1]>255:
			start[1]=0
			start[0]+=1
		if start[0]>255:
			print "One or more IP ranges have a higher starting IP than ending IP."
			sys.exit()
	list.append(str(start[0])+"."+str(start[1])+"."+str(start[2])+"."+str(start[3]))
	return list

#Takes IP in format xxx.xxx.xxx.xxx/xx and converts it into a dash-separated IP
#range.  Returns string with starting and ending IP.  This section acts as a
#basic subnetting calculator
def cidr_parser(ip_range):
	cidr = int(ip_range.split("/")[1])
	ip_octet_list = (ip_range.split("/")[0]).split(".")
	
	for x in range(0, 4):
		ip_octet_list[x] = int(ip_octet_list[x])
	bin_ip_octet_list = [0,0,0,0]
	
	for x in range(0, 4):
		bin_ip_octet_list[x] = '{0:08b}'.format(ip_octet_list[x])
	
	ip_octet_string = bin_ip_octet_list[0]+bin_ip_octet_list[1]+bin_ip_octet_list[2]+bin_ip_octet_list[3]
	ip_octet_string = ip_octet_string[0:cidr]+("1"*(32-cidr))
	ip_octet_string = [ip_octet_string[0:8],ip_octet_string[8:16],ip_octet_string[16:24],ip_octet_string[24:32]]
	
	for x in range(0, 4):
		ip_octet_string[x] = int(ip_octet_string[x], 2)
	end_ip = ip_octet_string
	
	bin_cidr_str = cidr*"1"+(32-cidr)*"0"
	bin_cidr_list = [bin_cidr_str[0:8],bin_cidr_str[8:16],bin_cidr_str[16:24],bin_cidr_str[24:32]]
	
	#calcualte start IP
	for x in range(0, 4):
		bin_cidr_list[x] = int(bin_cidr_list[x], 2)
	start_ip = [(bin_cidr_list[0] & ip_octet_list[0]),(bin_cidr_list[1] & ip_octet_list[1]),(bin_cidr_list[2] & ip_octet_list[2]),(bin_cidr_list[3] & ip_octet_list[3])]
	
	#convert int lists to final string to return to main function
	return str(start_ip[0])+"."+str(start_ip[1])+"."+str(start_ip[2])+"."+str(start_ip[3])+"-"+str(end_ip[0])+"."+str(end_ip[1])+"."+str(end_ip[2])+"."+str(end_ip[3])

	
def main():
	output_list = []
	
	#get file names of IP ranges and IPs to be excluded
	files = read_env_vars()
	
	#create list of IP ranges to calculate from the input file
	ranges = parse_raw_input(files[0])
	
	#iterate through ranges list and make everything dash-separated
	for x in range(0, len(ranges)):
		if "/" in ranges[x]:
			ranges[x] = cidr_parser(ranges[x])
			
	#iterate through the list and return expanded IP space
	for item in ranges:
		if "-" in item:
			expanded_range = range_splitter(item)
			for ip in expanded_range:
				output_list.append(ip)
		else:
			output_list.append(item)
	
	print "There are "+str(len(output_list))+" IP addresses in this list."
	number_of_files = raw_input("How many separate files to output? \nChoose a number between 1 and "+str(len(output_list))+":")
	number_of_files = int(number_of_files)
	while number_of_files < 1 or number_of_files > len(output_list):
		number_of_files = raw_input("Number not in range, please choose again:")
		number_of_files = int(number_of_files)
	
	#divide list into number_of_files specified by user
	ips_per_file = len(output_list)/number_of_files
	ips_counted_so_far = 0
	list_of_lists = []
	for x in range(0, number_of_files):
		tmp_list = []
		for y in range(ips_counted_so_far, ips_counted_so_far+ips_per_file):
			tmp_list.append(output_list[y])
		if ips_counted_so_far+(ips_per_file*2)>len(output_list):
			for z in range(ips_counted_so_far+ips_per_file, len(output_list)):
				tmp_list.append(output_list[z])
				print output_list[z]
		ips_counted_so_far+=ips_per_file
		list_of_lists.append(tmp_list)
	
	#output to files
	for o in range(0, len(list_of_lists)):
		filename = "ip_range_"+str(o+1)+".txt"
		file = open(filename, 'w')
		for ip in list_of_lists[o]:
			file.write(ip+"\n")
		file.close()

if __name__ == "__main__":
	main()