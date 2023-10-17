# Cataloguing-NACO-special-projects
Tools developed to support Name Authority Cooperative program (NACO) special projects initiated by NLNZ.

## Adding identifiers to targeted NACO records

The following scripts were used to create a workflow to add identifiers to NACO personal name records in a semi automated way.

- **Access_point_counter.py** - Opens a MARC bibliographic file, and creates a list of all personal name access points from the 100 and 700 fields, 
then counts the specified number of highest occurring access points. Outputs a CSV file of results. Used to identify prolific creators and contributors.

- **Check_access_points_get_identifiers.py** - Opens the CSV list of access points, and searches each access point against id.loc.gov label search for an exact match – where it matches it resolves to the entity page (e.g. https://id.loc.gov/authorities/names/n50018766.html). It checks if the record is catalogued under RDA or not in the associated MARC XML and it checks for existing identifiers in 024. It then queries VIAF by LCCN, and looks for VIAF, ISNI and Wikidata identifiers that do not already exist in the authority record.
    It will output:
    - A Excel spreadsheet summarising the results (name using spreadsheet_filename variable)
    - output_VIAF_IDs.txt – all the related identifiers found in one file
    - output_VIAF_IDs_1_todays_date.txt – splits file above into multiple files of up to 50 lines long, to be used in Connexion Client with the Bulk Changer macro.
    - output_different_ids.txt – any differences of identifiers found between id.loc.gov and VIAF.
    - output_existings.txt – any records that have the selected identifiers already in id.loc.gov.

- **Check_LCCNs_get_identifiers.py** - Opens a CSV file of LCCNs, and retrieves the id.loc.gov page, getting the access point. It checks if the record is catalogued under RDA or not in the MARC XML file (e.g. https://id.loc.gov/authorities/names/n50018766.marcxml.xml). If it is RDA, it then reads the published MARC file to check for existing identifiers. It checks if the record is catalogued under RDA or not in the associated MARC XML and it checks for existing identifiers in 024. It then queries VIAF by LCCN, and looks for VIAF, ISNI and Wikidata identifiers that do not already exist in the authority record.
    It will output:
    - A Excel spreadsheet summarising the results (name using spreadsheet_filename variable)
    - output_VIAF_IDs.txt – all the related identifiers found in one file
    - output_VIAF_IDs_1_todays_date.txt – splits file above into multiple files of up to 50 lines long, to be used in Connexion Client with the Bulk Changer macro.
    - output_different_ids.txt – any differences of identifiers found between id.loc.gov and VIAF.
    - output_existings.txt – any records that have the selected identifiers already in id.loc.gov.

- **Bulk Changer macro** - Runs in Connexion Client. Opens files created by the two get_identifier scripts, iterates line by line getting LCCN numbers and information to add. Opens, locks, saves records to local file. Adds info.
