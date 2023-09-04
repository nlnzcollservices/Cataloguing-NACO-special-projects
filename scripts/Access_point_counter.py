import csv
import re
import os
import string
from pymarc import MARCReader, Record, Field
from collections import Counter

"""Opens a a MARC bibliographic file, and creates a list of all personal name access points from the 100 and 700 fields, 
then counts the specified number of highest occurring access points. Outputs a CSV of results."""

def get_APs(filename):
    #creates a text file to record all occurences of access points
    with open('APresults.txt', 'wt', encoding='utf-8-sig', newline = '') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter = "\t")
        #opens and reads marc file
        with open (filename, 'rb') as file:
                marcfile = MARCReader(file, to_unicode=True, force_utf8=True,)
                #loop through records
                for record in marcfile:
                    #print(record.title)
                    #regex pattern finds ending initials that lack full stops as a result of rstrip
                    pattern = '\s[a-zA-Z]$'
                    #try and get a 100 field
                    try:
                        APperson = record.get_fields('100')[0]
                        #use specific subfields only
                        APperson = ' '.join(APperson.get_subfields('a', 'c', 'q', 'd'))
                        #hard removal final punctuation in string
                        APperson = APperson.strip().strip(',.')

                        #adds back full stop for single letters (assumption this is mostly going to be an initial)
                        try:
                            #gets final initial
                            replacement = re.findall(pattern, APperson)[0] + "."
                            #substitutes replacement 
                            APperson = re.sub(pattern, replacement, APperson)
                            #write it out
                            spamwriter.writerow([APperson])
                        #APs that don't end with single letter (most)
                        except:
                            spamwriter.writerow([APperson])
                            
                    except:
                        pass
                    
                    #try and get 700 field(s)
                    try:
                        APperson7xxs = record.get_fields('700')
                        for APperson7xx in APperson7xxs:
                            #checking for $t
                            APperson7xxt = APperson7xx.get_subfields('t')
                            #use specific subfields only
                            APperson7xx = ' '.join(APperson7xx.get_subfields('a', 'c', 'q', 'd'))
                            #checking if there no $t subfield (excluding these from the count):
                            if str(APperson7xxt) == '[]':                            
                                APperson7xx = APperson7xx.strip().strip(',.')

                                #adds back full stop for single letters (this is mostly going to be an initial)
                                try:                                
                                    replacement = re.findall(pattern, APperson7xx)[0] + "."
                                    APperson7xx = re.sub(pattern, replacement, APperson7xx)
                                    spamwriter.writerow([APperson7xx])
                                 #APs that don't end with single letter (most)
                                except:
                                    spamwriter.writerow([APperson7xx])
 
                    except:
                        pass


def count_APs(top_access_points):
    #open text file with all access points and creates a dictionary with counting each occurrence of access point.
    with open('APresults.txt', "r", encoding='utf-8-sig', newline = '') as f:
        lines = f.readlines()
        AP_and_count_dict = Counter(lines).most_common(top_access_points)
        return AP_and_count_dict


def write_results(AP_and_count_dict, top_access_points):
    #write out access point and count results as csv
    csv_filename = "Top_" + str(top_access_points) + "_APs.csv"
    header = ['Access point', 'Count']
    with open(csv_filename, 'wt', encoding='utf-8-sig', newline = '') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter = ",")
        spamwriter.writerow(header)
        for pair in AP_and_count_dict:
           apname = pair[0].replace('\r\n', '') 
           apcount = pair[1]
           spamwriter.writerow([apname, apcount]) 


#################################################################################
# Main 
#################################################################################

def main():
    #open this marc file:
    filename = 'PubsNZApr23.mrc'
    #get all APs and build txt file of list
    get_APs(filename)
    #list size:
    top_access_points = 500
    #count APs creating a dictionary
    AP_and_count_dict = count_APs(top_access_points)
    #Write results file
    write_results(AP_and_count_dict, top_access_points)
    #delete working file of all occurences of access points (otherwise append will keep adding to the file next time it is run)
    os.remove('APresults.txt')

if __name__ == "__main__":
    main()