'''
CSV to TypeQL Insert Script

Execute like this:

python3 csv_to_tql.py /path/to/input_csv.csv output_csv_name.csv

'''
from ast import literal_eval
import pandas as pd
import sys

source_file = sys.argv[1]

print(f"You are pulling data in from {source_file}")

# Must use dtype=object to avoid pandas coercing integers to floats
df = pd.read_csv(source_file, dtype=object)

# Scrub out any .x trailing chracters in column names
# We need to preserve the ability to have duplicated colum names
# for hyper-edges where multiple entities have the same role type
df.columns = df.columns.str.split('.').str[0].tolist()

row_iterator = 0 # keep track of which row we are processing

insert_query_strings = [] # we will hold our resulting insert queries here

# For each row
for i, r in df.iterrows():
    r = r.dropna() # get rid of all the NaN fields for that row
    # We need a list that is purely attribute names (the x "has y" pieces of the query)
    attributes = r.index.tolist()
    attributes = [x for x in attributes if x not in ['ent_or_rel','sub_type','alias']]

    '''
    Now based on these column attributes & values,
    we form our tql strings
    '''
    
    ############################################
    ######        HANDLE ENTITIES          #####
    ############################################
    if "ent" in r['ent_or_rel'].lower():
        #print("ENTITY query detected")
        try:
            query = f'{r["alias"]} isa {r["sub_type"]}, ' # first, we use sub_type & alias columns
        except:
            print("Need to have a sub_type (what kind of entity) and an alias (the $var you use to refer to it in typeDB)")
            break
        
        if len(attributes) > 0: # if this entity has attributes...
            # For each other row, we iteratively add the other key:value pieces (the x has y tql parts)
            for attrib in attributes:
                # Try to coerce an attribute to its apparent type
                try:
                    attrib_alt = literal_eval(r[attrib])
                except:
                    #print(f"failed coercion for {r[attrib]} in row {row_iterator}. Treating as string.")
                    attrib_alt = r[attrib]
                
                # Strings need quotes around them
                if type(attrib_alt) == str:
                    query = query + f'has {attrib} "{attrib_alt}", '
                
                # If it's not a string, we just push the raw value
                # unless it's a boolean; then we convert to string, make it lowercase, and put it in without-quotes
                else:
                    if type(attrib_alt) == bool:
                        bool_val = str(r[attrib]).lower()
                        query = query + f'has {attrib} {bool_val}, '    
                    else:
                        query = query + f'has {attrib} {attrib_alt}, '

            # Replace the final comma with a semicolon
            query = query[:-2] + ';'
            insert_query_strings.append(query)
        else:
            query = query[:-2] + ';'
            insert_query_strings.append(query)

    ############################################
    ######        HANDLE RELATIONS         #####
    ############################################
    elif "rel" in r['ent_or_rel'].lower():
        #print("RELATION query detected")
        
        # These will hold the detected roles & the variables pointing at the entities
        # that play those roles
        roles = []
        role_variables = []

        # generate base query $alias ([playrole1]: [$x], [playrole2]: [$y]) isa [relation_sub_type]
        base_query = f'{r["alias"]}'
        # To get the connecting aliases, we filter for the values starting with $ in this row
        sub_iter = 0
        for val in r[attributes]:
            try:
                if val.startswith("$"):
                    roles.append(attributes[sub_iter])
                    role_variables.append(val)
            except:
                pass
            sub_iter += 1
        
        # If there aren't enough roles to make a relationship,
        # print a message to let the user know where the problem is
        if len(roles) < 2:
            print(f"Need 2 variables pointing at entities (e.x. $a and $b) to create a relationship! Check row {row_iterator}")
            break
        else:
            role_string = ' ('
            for role in range(0,len(roles)):
                role_string = role_string + f'{roles[role]}:{role_variables[role]}, '
            
            role_string = role_string[:-2] + f') isa {r["sub_type"]};'

            base_query = base_query + role_string

            # If the relationship has attributes, we now add those to the rel insert query
            # To test if this is needed, we check to see how many attributes are in this row
            # other than the $ attributes
            remaining_attributes = [x for x in attributes if x not in roles]

            # anything left in this list must be an attribute
            if len(remaining_attributes) > 0:
                # replace the semicolon from the end of the base query with a comma
                base_query = base_query[:-1] + ', '
                
                for attrib in remaining_attributes:
                    # Try to coerce an attribute to its apparent type
                    try:
                        attrib_alt = literal_eval(r[attrib])
                    except:
                        #print(f"failed coercion for {r[attrib]} in row {row_iterator}. Treating as string.")
                        attrib_alt = r[attrib]
                    # If it's a string attribute, we need to put quotes around it
                    if type(attrib_alt) == str:
                        base_query = base_query + f'has {attrib} "{attrib_alt}", '
                    else:
                        # If it's a boolean value, convert to lowercase string + insert sans-double-quotes
                        if type(attrib_alt) == bool:
                            bool_val = str(r[attrib]).lower()
                            base_query = base_query + f'has {attrib} {bool_val}, '
                        else:
                            # otherwise, we push the raw value
                            base_query = base_query + f'has {attrib} {attrib_alt}, '
                # Replace the final comma with a semicolon
                base_query = base_query[:-2] + ';'
                # Capture the insert query
                insert_query_strings.append(base_query)

            # If there are no attributes to this relation, we just use the base query
            else:
                insert_query_strings.append(base_query)

    # Print message letting user know the row has no valid field
    else:
        print(f"No relation/entity identifier for {row_iterator}. Skipping...")

    row_iterator += 1 # increment counter for each row

print(
    f"Insertion statements for {len(df)} entities & relationships will be made")

with open(sys.argv[2], "w") as outfile:
    outfile.write("insert\n")
    for element in insert_query_strings:
        outfile.write(element + "\n")

print(f'''You can now use {sys.argv[2]} to write to your database!

1) Access your TypeQL Console
2) > transaction <database_name> schema write
3) > source /path/to/{sys.argv[2]}
4) > commit
''')
