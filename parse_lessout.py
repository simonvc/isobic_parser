import re
import json


def capture_groups(lines):
    groups = {
        'creation_date': (0, 10),
        'update_date': (13, 10),
        'bic': (24, 10),
        'brch': (37, 3),
        'legal_name': (40, 43),
        'registered_address': (83, 40),
        'operational_address': (123, 40),
        'branch_description': (163, 20),
        'branch_address': (183, 40),
        'instit': (223, 8)
    }


    
    result = {}
    for key, (start, length) in groups.items():
        value = " ".join(line[start:start+length].strip() for line in lines)
        result[key] = re.sub(r'\s{2,}', ' ', value)
    
    return result

file_name="less_out.txt"

# for each line, assume we're not in a record until we find 2 dates in the columns creation_date and update_date
# then we're in a record. extract the fields, subsequent lines extract the columns for registered_address, operational_address, and branch_address
# and add them to the registered_address, operational_address, and branch_address variables
# occasionally we will have a header rows, which start with CTRL-LRecord, creation, date, we should skip these lines.

lines=open(file_name).readlines()

records=[]
record=[]

in_record=False

for line in lines:
    if in_record != True:
        record=[]
    if line.startswith('Record'):  # Skip header rows
        in_record=False
        continue
    if line.startswith(''):  # Skip header rows
        in_record=False
        continue
    if line.startswith('creation'):  # Skip header rows
        in_record=False
        continue
    if line.startswith('date'):  # Skip header rows
        in_record=False
        continue
    #check if the record starts with the regex or date 'dddd-dd-dd'
    if re.match(r'^\d{4}-\d{2}-\d{2}', line):
       in_record=True
       records.append(record) #old record
       record=[] #start new record
       record.append(line)
    else:
        if in_record:
            record.append(line)


banks=[]
for record in records:
    try:
        data=capture_groups(record)
        banks.append(data)
    except IndexError:
        continue
    


#save banks as csv and json files

print(banks[0:10])

bic_indexed_data = {}
for item in banks:
    bic = item['bic'].strip()  # Remove leading/trailing whitespace
    if bic:  # Only add items with non-empty BIC
        bic_indexed_data[bic] = item

# Save the new dictionary as a JSON file
with open('bic_indexed_data.json', 'w') as f:
    json.dump(bic_indexed_data, f, indent=2)
