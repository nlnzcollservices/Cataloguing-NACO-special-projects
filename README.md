# Cataloguing-NACO-special-projects
Tools developed to support Name Authority Cooperative program (NACO) special projects initiated by NLNZ.

- **Access_point_counter.py** - Opens a MARC bibliographic file, and creates a list of all personal name access points from the 100 and 700 fields, 
then counts the specified number of highest occurring access points. Outputs a CSV file of results. Used to identify prolific creators and contributors.

- **Bulk Changer macro ** - Runs in Connexion Client. Opens file created by Access_point_counter.py, iterates line by line getting LCCN numbers and information to add. Opens, locks, saves records to local file. Adds info.
