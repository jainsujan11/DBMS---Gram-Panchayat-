query_select="select citizen_id,name,gender,dob,household_id,educational_qualification"
query_from="from Citizen "
query_where="where 1=1"
query_group_by="group by citizen_id,name,gender,dob,household_id,educational_qualification"
query_having="having 1=1"
group_by=0

name="ashish"
gender="M"
edu="10th"
min_land=12
max_income=23
dob='2003.10.13'
is_pradhan=None
is_employee=None
vacc_year=2024


params = []
if name:
    query_where+=" AND name ILIKE "+name


if gender and gender != "Any":
    query_where += " AND gender = "+gender
if edu:
    # query += " AND educational_qualification ILIKE %s"
    query_where += " AND educational_qualification ILIKE "+edu
if min_land:
    query_select+=",sum(area_acres)"
    query_from+=" natural join land_records using (citizen_id)"
    query_having+=" and sum(area_acres) >= 1.5"
    group_by=1
if max_income:
    query_select+=",income"
    query_from+=" natural join households using (household_id)"
    query_having+=" and income <= 100"
    group_by=1
if dob:
    query_where += " AND dob = 2003.10.13"
if is_pradhan == 'on':
    query_from  +=" natural join panchayat_employees using (citizen_id)"
    query_where += " AND role = 'Pradhan'"
if is_employee == 'on':
    if is_pradhan != 'on':
        query_select += ",role"
        query_from += " natural join panchayat_employees using (citizen_id)"
if vacc_year:
    query_select+=",date_adminstered"
    query_from += "natural join vaccinations using (citizen_id)"
    query_where += " AND date_administered >= '2024.01.01' AND date_administered < '2025.01.01'"
    params.append(vacc_year)
    params.append(vacc_year)

query=query_select+"\n"+query_from+"\n"+query_where
if(group_by):
    query+="\n"+query_group_by+"\n"+query_having

print(query)


