from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('localhost', 27017) 
db = client.get_database('BDProject') 

projects = db.projects
technologies = db.technologies
countries = db.countries
investments = db.investments
productions = db.productions

# إنشاء الفهارس (Indexes)
db.countries.create_index([("name", 1)], name="country_name_index")

db.technologies.create_index([("Technology", 1)], name="tech_name_index")

db.projects.create_index([("status", 1)], name="project_status_index")
db.projects.create_index([("product", 1)], name="product_index")
db.projects.create_index([("LOWE_CF", 1)], name="lowe_cf_index")

db.productions.create_index([("project_id", 1)], name="production_project_id_index")

db.projects.create_index([("latitude", 1), ("longitude", 1)], name="geo_location_index")

db.projects.create_index([("status", 1), ("date_online", -1)], name="status_date_index")

db.projects.create_index([("technology_ids", 1), ("product", 1)], name="tech_product_index")

db.projects.create_index([("technology_ids", 1)], name="multikey_tech_ids_index")

db.technologies.create_index([("project_ids", 1)], name="multikey_project_ids_index")

db.productions.create_index(
    [("project_id", 1), ("announced_size", -1)],
    background=True,
    name="compound_project_announced_size_index"
)
