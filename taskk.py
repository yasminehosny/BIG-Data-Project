import pandas as pd
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime


client = MongoClient("mongodb://localhost:27017/")

db = client["BDProject"]


df = pd.read_csv("C:\\ALL IN ONE\\Downloads\\project.csv")  



# 1. countries Collection
# ----------------------
country_name_to_id = {}
for country_name in df['Country'].dropna().unique():
    country_doc = {"name": country_name}
    country_id = db.countries.insert_one(country_doc).inserted_id
    country_name_to_id[country_name] = country_id

# ----------------------
# 2. technologies Collection
# ----------------------
technology_signature_to_id = {}
technology_fields = ['Technology', 'Technology_details', 'Technology_electricity', 'Technology_electricity_details', 'Technology_aggregate']
technologies = df[technology_fields].drop_duplicates().dropna(subset=['Technology'])

for _, row in technologies.iterrows():
    tech_signature = tuple(row[col] for col in technology_fields)
    tech_doc = {
        col: row[col] for col in technology_fields
    }
    tech_doc["project_ids"] = []  

    tech_id = db.technologies.insert_one(tech_doc).inserted_id
    technology_signature_to_id[tech_signature] = tech_id



# ----------------------
# 3. projects Collection 
# ----------------------

projects_ids = []

for idx, row in df.iterrows():
    if pd.isna(row['Project name']):
        continue

    country_id = country_name_to_id.get(row['Country'])

    
    tech_signature = tuple(row.get(col) for col in technology_fields)
    tech_id = technology_signature_to_id.get(tech_signature)

    technology_ids = [tech_id] if tech_id else []

    try:
       
        project_doc = {
            "name": str(row['Project name']),
            "country_id": country_id,
            

            "date_online": datetime(year=int(row['Date online']), month=1, day=1) if pd.notna(row['Date online']) else None,
            

            "status": str(row['Status']) if pd.notna(row['Status']) else "Unknown",
            "latitude": float(row['Latitude']) if pd.notna(row['Latitude']) else 0.0,
            "longitude": float(row['Longitude']) if pd.notna(row['Longitude']) else 0.0,
            "LOWE_CF": float(row['LOWE_CF']) if pd.notna(row['LOWE_CF']) else 0.0,
            "product": str(row['Product']) if pd.notna(row['Product']) else "Unknown",
            "technology_ids": technology_ids 
        }

        project_id = db.projects.insert_one(project_doc).inserted_id
        projects_ids.append((idx, project_id))

        
        if tech_id:
            db.technologies.update_one(
                {"_id": tech_id},
                {"$addToSet": {"project_ids": project_id}}  
            )

    except Exception as e:
        print(f"Error inserting project at index {idx}: {e}")
        continue

# 4. productions Collection 
# ----------------------
production_fields = ['Capacity_MWel', 'Capacity_Nm\u00b3 H\u2082/h', 'Capacity_kt H2/y', 'Capacity_t CO\u2082 captured/y', 'IEA zero-carbon estimated normalized capacity [Nm\u00b3 H\u2082/hour]']
for idx, row in df.iterrows():
    production_data = {field: row.get(field) for field in production_fields}
    
    announced_size = row.get('Announced Size')
    if announced_size:
        production_data["announced_size"] = announced_size
    if all(pd.isna(value) for value in production_data.values()):
        continue
    project_id = projects_ids[idx][1]
    production_data["project_id"] = project_id
    db.productions.insert_one(production_data)