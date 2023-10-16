import requests
import csv
import time
import os
import io
from bs4 import BeautifulSoup
import json
from qwikidata.entity import WikidataItem, WikidataLexeme, WikidataProperty
from qwikidata.linked_data_interface import get_entity_dict_from_api
from openpyxl import Workbook,load_workbook
from datetime import date

""" Opens CSV of LCCNs and finds each authority record on id.loc.gov. It then checks for identifiers in VIAF and outputs 
text files (up to 50 lines long) that can be used in automated process in Connexion, and also outputs a summary spreadsheet,
and a text file with any identifiers that don't match between LCNAF and VIAF"""

#looks up access point  
def Check_AP_LOC(lccn):
    BASE_PR_URL = 'http://id.loc.gov/authorities/names/'

    full_query = (BASE_PR_URL + lccn + ".html")
    print(full_query)


    r = requests.get(full_query,verify=False)
    #reponse 200
    if r.status_code == 200:
        #bs4 to get URL
        soup = BeautifulSoup(r.text, "html.parser")
        time.sleep(2)
        LCpagetext = soup.get_text()
        founddiv = soup.find("span", { "property" : "madsrdf:authoritativeLabel skos:prefLabel" })

        lcnafAP = founddiv.contents[0]
        #get ID from URL
        found = "Y"
        #call next function
        Check_ID_LOC_info(lccn, lcnafAP, found)

    if r.status_code == 404:
        found = "N"
        lccn = ""
        #add to spreadsheet
        sheet.append(["LCCN not found", found])
        wb.save(spreadsheet_filename)

#checks LCNAF authority record
def Check_ID_LOC_info(lccn, lcnafAP, found):
    recordmarcURL = "https://id.loc.gov/authorities/names/" + lccn + ".marcxml.xml"
    r = requests.get(recordmarcURL, verify=False)
    soupa = BeautifulSoup(r.text, "html.parser")
   
    #is it RDA?  now checking for identifiers regardless
    f040 = soupa.find("marcxml:datafield", {"tag" : "040"})
    is_it_rda = f040.find("marcxml:subfield", {"code" : "e"})
    if not is_it_rda == None:
        subfield_e = is_it_rda.contents[0]
        if subfield_e == "rda":
            RDArecord = "Y"
        else:
            RDArecord = "N"
    else:
        #record is not RDA
        RDArecord = "N"

    # create dictionary for existing identifiers in id.loc.gov
    id_dict = {"wikidata": "", "isni": "", "viaf": ""} 
    #check for existing identifiers in id.loc.gov marc xml
    f024s = soupa.find_all("marcxml:datafield", {"tag" : "024"})
    if not f024s == None:
        for f024 in f024s:
            idsource = f024.find("marcxml:subfield", {"code" : "2"})
            if idsource == None:
                try:
                    id_item = f024.find("marcxml:subfield", {"code" : "1"}).contents[0]
                    if "viaf" in id_item:
                        id_item_id = id_item.split("/")[-1]
                        id_dict["viaf"] = id_item_id
                    if "wikidata" in id_item:
                        id_item_id = id_item.split("/")[-1]
                        id_dict["wikidata"] = id_item_id
                    if "isni" in id_item:
                        id_item_id = id_item.split("/")[-1]
                        id_dict["isni"] = id_item_id
                except:
                    print(str(f024))
                    
            #is there wikidata identifier?
            elif idsource.contents[0] == 'wikidata':
                id_item = f024.find("marcxml:subfield", {"code" : "a"}).contents[0]
                #add wikidata item to dictionary
                id_dict["wikidata"] = id_item
            #is there isni identifier?
            elif idsource.contents[0] == 'isni':
                id_item = f024.find("marcxml:subfield", {"code" : "a"}).contents[0]
                #add isni item to dictionary
                id_dict["isni"] = id_item
            #is there viaf identifier?
            elif idsource.contents[0] == 'viaf':
                id_item = f024.find("marcxml:subfield", {"code" : "a"}).contents[0]
                #add viaf item to dictionary
                id_dict["viaf"] = id_item

            elif idsource.contents[0] == 'uri':
                id_item = f024.find("marcxml:subfield", {"code" : "a"}).contents[0]
                #add viaf item to dictionary
                if "viaf" in id_item:
                    id_item_id = id_item.split("/")[-1]
                    id_dict["viaf"] = id_item_id
                if "wikidata" in id_item:
                    id_item_id = id_item.split("/")[-1]
                    id_dict["wikidata"] = id_item_id
                if "isni" in id_item:
                    id_item_id = id_item.split("/")[-1]
                    id_dict["isni"] = id_item_id
            else:
                print(str(f024))
    #print(id_dict)

    #call viaf check - takes dictionary to compare.
    Check_VIAF(lccn, lcnafAP, found, id_dict, RDArecord)


def Check_VIAF(lccn, lcnafAP, found, id_dict):

    #scope status
    RDArecord = "Y"

    #get the links to clustered identifiers
    urllc = "https://www.viaf.org/viaf/lccn/" + lccn + '/justlinks.json' 

    r = requests.get(urllc, verify=False)
    j = json.loads(r.text)

    #get the viaf identifier and prefix 
    viaf = ",viaf:" + j["viafID"]
    #check for identifier in existing record, if there is it change viaf to "" to ensure nothing is added to output txt file
    if not id_dict["viaf"] == "":
        viaf = ""

    try:
        #try and get the wikidata identifier and prefix
        wikidata = ",wikidata:" + j["WKP"][0]
        #calls wikidata API to get a label
        wikiid_dict = get_entity_dict_from_api(j["WKP"][0])
        wikilabel = wikiid_dict["labels"]["en"]["value"]
        #check for identifier in existing record, if there is it change wikidata to "" to ensure nothing is added to output txt file
        if not id_dict["wikidata"] == "":
            wikidata = ""
            #checks for case of differing identifiers between viaf and id.gov.loc
            if not id_dict["wikidata"] == j["WKP"][0]:
                output_different_ids = open("output_different_ids.txt","a", encoding="utf-8")
                output_different_ids.write(lccn + " and " + j["viafID"] + " have different wikidata identifiers." + "\n")
        
    except KeyError:
        wikidata = ""
        wikilabel = ""

    try:
        #try and get the isni identifier and prefix
        isni = ",isni:" + j["ISNI"][0]
        #check for identifier in existing record, if there is it change isni to "" to ensure nothing is added to output txt file
        if not id_dict["isni"] == "":
            isni = ""
            #checks for case of differing identifiers bbetween viaf and id.gov.loc
            if not id_dict["isni"] == j["ISNI"][0]:
                output_different_ids = open("output_different_ids.txt","a", encoding="utf-8")
                output_different_ids.write(lccn + " and " + j["viafID"] + " have different wikidata identifiers." + "\n")

    except KeyError:
        isni = ""
        isnilabelcon = ""
    
    #if all identifies are empty strings - the ids already exist and / or there are new identifiers to add
    if isni == wikidata == viaf == "":
        output_existing = open("output_existings.txt","a", encoding="utf-8")
        output_existing.write(lccn + " already has the available identifiers found on viaf." + "\n")
    
    #outputs file for Connexion macro - it is outputting only those available on viaf, and not already in id.loc.gov records
    else:
        output_viaf = open("output_VIAF_IDs.txt","a")
        output_viaf.write(lccn + viaf + isni + wikidata + "\n")

    time.sleep(1) 
    
    #add to spreadsheet
    sheet.append([lcnafAP, found, lccn, RDArecord, str(id_dict), viaf + isni + wikidata, wikilabel])
    wb.save(spreadsheet_filename)

    print(lccn, viaf, isni, wikidata)
  
def Split_and_count():
    
    try:
        #open output file and count identifiers found, split file into multiple
        with open('output_VIAF_IDs.txt', "r", encoding='utf-8-sig') as g:
            idsoutputed = g.readlines()
            lcncount = 0
            viafcount = 0
            wikicount  = 0
            isnicount = 0
            filecount = 0
            fiftylst = []
            todaysdate = str(date.today())
            for line in idsoutputed:
                lcncount = lcncount + 1
              
                if 'wikidata' in line:
                    wikicount = wikicount + 1
                if 'viaf' in line:
                    viafcount = viafcount + 1
                if 'isni' in line:
                    isnicount = isnicount + 1
                fiftylst.append(line)
                #output txt file at 50 list items
                if len(fiftylst) == 50:
                    filecount = filecount + 1
                    subfilename = "output_VIAF_IDs_" + str(filecount) + "_" + todaysdate + '.txt'
                    output_viaf = open(subfilename,"a")
                    output_viaf.write(''.join(fiftylst))
                    output_viaf.close()

                    fiftylst = []
            #output file for any remaining in the list, but less the 50
            filecount = filecount + 1
            subfilename = "output_VIAF_IDs_" + str(filecount) + "_" + todaysdate + '.txt'
            output_viaf = open(subfilename,"a")
            output_viaf.write(''.join(fiftylst))
            output_viaf.close()

        print("total: ", lcncount)
        print("viaf:", viafcount)
        print("wikidata:", wikicount)
        print("isni:", isnicount)

    except:
        print('Possibly no text file to split, meaning no new identifiers to add')

#################################################################################
# Main 
#################################################################################

#create spreadsheet that gives overview of results
spreadsheet_filename = 'LCCN_based_identifier_check_results_28-06-23.xlsx'
header = ['LCNAF AP', 'Authority Found', 'LCNAF ID', 'RDA', 'LCNAF existing ids from 024', 'VIAF ids to add', 'Wikidata label']  
wb = Workbook()
sheet = wb.active
sheet.append(header)

def main():
    
    #edit name of file of access points to open
    csvfilename = "LCCNs.csv"
    #open  txt file with access points
    with open(csvfilename,  'r', encoding='utf-8-sig') as csvopen: 
        csvreader = csv.reader(csvopen)
        for row in csvreader:
            lccn = (row[0])
            print(lccn)
            Check_AP_LOC(lccn)
    
    #split and count files
    Split_and_count()

if __name__ == "__main__":
    main()     
