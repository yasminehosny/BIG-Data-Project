import streamlit as st
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from bson.code import Code
from collections import defaultdict



# تحديد إعدادات الصفحة في البداية
st.set_page_config(page_title="MongoDB CRUD Interface", layout="wide")

# الاتصال بقاعدة البيانات
client = MongoClient("mongodb://localhost:27017")
db = client["BDProject"]

projects = db.projects
technologies = db.technologies
countries = db.countries
productions = db.productions  

# عنوان الصفحة
st.title("project Interface")

def insert_document(table, data):
    return db[table].insert_one(data).inserted_id

def update_document(table, filter_cond, update_data):
    return db[table].update_many(filter_cond, {"$set": update_data}).modified_count

def delete_document(table, filter_cond):
    return db[table].delete_many(filter_cond).deleted_count

# ─── Streamlit UI ────────────────────────────────────────────────────────────
table = st.sidebar.selectbox("Select Collection", ["countries", "technologies", "projects", "productions"])
operation = st.sidebar.selectbox("Select Operation", ["Insert", "Update", "Delete"])
# INSERT Form
if operation == "Insert":
    with st.form("insert_form"):
        if table == "countries":
            name = st.text_input("Country Name")
            submitted = st.form_submit_button("Insert")
            if submitted and name:
                _id = insert_document(table, {"name": name})
                st.success(f"Inserted Country with ID: {_id}")

        elif table == "technologies":
            tech = st.text_input("Technology")
            tech_details = st.text_input("Technology_details")
            elec = st.text_input("Technology_electricity")
            elec_details = st.text_input("Technology_electricity_details")
            agg = st.text_input("Technology_aggregate")
            submitted = st.form_submit_button("Insert")
            if submitted and tech:
                doc = {
                    "Technology": tech,
                    "Technology_details": tech_details,
                    "Technology_electricity": elec,
                    "Technology_electricity_details": elec_details,
                    "Technology_aggregate": agg,
                    "project_ids": []
                }
                _id = insert_document(table, doc)
                st.success(f"Inserted Technology with ID: {_id}")

        elif table == "projects":
    # إدخال البيانات من المستخدم
            name = st.text_input("Project Name")
            country_name = st.text_input("Country Name")
            product = st.text_input("Product")
            status = st.text_input("Status")
            date_online = st.number_input("Date Online", format="%.1f")
            
            latitude = st.number_input("Latitude", format="%.6f")
            longitude = st.number_input("Longitude", format="%.6f")
            lowe_cf = st.number_input("LOWE_CF", format="%.2f")  # عامل خفض الانبعاثات
            tech_name = st.text_input("Technology Name (to link)")  # رابط للتكنولوجيا

            submitted = st.form_submit_button("Insert")
            if submitted and name:
        # البحث عن البلد والتكنولوجيا
                c = db.countries.find_one({"name": country_name})
                t = db.technologies.find_one({"Technology": tech_name})
                try:
           
                    doc = {
                    "name": name,
                    "country_id": c["_id"] if c else None,
                    "status": status,
                    "latitude": latitude,
                    "longitude": longitude,
                    "date_online": date_online,
                    
                    "product": product,
                    "LOWE_CF": lowe_cf,  # إضافة الحقل الجديد
                    "technology_ids": [t["_id"]] if t else []  # ربط المشروع بالتكنولوجيا
                 }

            # إدخال الوثيقة في قاعدة البيانات
                    pid = insert_document(table, doc)

            # تحديث جدول التكنولوجيا لربطها بالمشروع
                    if t:
                        db.technologies.update_one({"_id": t["_id"]}, {"$addToSet": {"project_ids": pid}})

            # إظهار رسالة نجاح
                    st.success(f"Inserted Project with ID: {pid}")
                except Exception as e:
                    st.error(f"Error: {e}")


        elif table == "productions":
            project_name = st.text_input("Project Name (to link)")
            cap_mwel = st.number_input("Capacity MWel", format="%.2f")
            cap_nmh2 = st.number_input("Capacity Nm³ H₂/h", format="%.2f")
            cap_kt_h2 = st.number_input("Capacity kt H2/y", format="%.2f")
            cap_t_co2 = st.number_input("Capacity t CO₂ captured/y", format="%.2f")
            iea_cap = st.number_input("IEA Normalized Capacity [Nm³ H₂/hour]", format="%.2f")
            announced_size = st.number_input("Announced Size (MWel)", format="%.2f")
   
            submitted = st.form_submit_button("Insert")
            if submitted:
                p = db.projects.find_one({"name": project_name})
                try:
                    doc = {
                    "project_id": p["_id"] if p else None,
                    "Capacity_MWel": cap_mwel,
                    "Capacity_Nm³ H₂/h": cap_nmh2,
                    "Capacity_kt H2/y": cap_kt_h2,
                    "Capacity_t CO₂ captured/y": cap_t_co2,
                    "IEA zero-carbon estimated normalized capacity [Nm³ H₂/hour]": iea_cap,
                    "Announced_Size_MWel": announced_size  # إضافة العمود الجديد
                    }
                    _id = insert_document(table, doc)
                    st.success(f"Inserted Production with ID: {_id}")
                except Exception as e:
                    st.error(f"Error: {e}")

elif operation == "Update":
    with st.form("update_form"):
        if table == "countries":
            old_name = st.text_input("Existing Country Name")
            new_name = st.text_input("New Country Name")
            submitted = st.form_submit_button("Update")
            if submitted and old_name and new_name:
                result = db.countries.update_one({"name": old_name}, {"$set": {"name": new_name}})
                if result.modified_count:
                    st.success("Country updated successfully.")
                else:
                    st.warning("No matching country found or no change made.")

        elif table == "technologies":
            old_tech = st.text_input("Existing Technology Name")
            new_tech = st.text_input("New Technology Name")
            new_details = st.text_input("New Technology Details")
            submitted = st.form_submit_button("Update")
            if submitted and old_tech:
                result = db.technologies.update_one(
                    {"Technology": old_tech},
                    {"$set": {
                        "Technology": new_tech,
                        "Technology_details": new_details
                    }}
                )
                if result.modified_count:
                    st.success("Technology updated successfully.")
                else:
                    st.warning("No matching technology found or no change made.")

        elif table == "projects":
            old_name = st.text_input("Existing Project Name")
            new_name = st.text_input("New Project Name")
            new_status = st.text_input("New Status")
            new_product = st.text_input("New Product")
            submitted = st.form_submit_button("Update")
            if submitted and old_name:
                result = db.projects.update_one(
                    {"name": old_name},
                    {"$set": {
                        "name": new_name,
                        "status": new_status,
                        "product": new_product
                    }}
                )
                if result.modified_count:
                    st.success("Project updated successfully.")
                else:
                    st.warning("No matching project found or no change made.")

        elif table == "productions":
            project_name = st.text_input("Project Name (to identify production)")
            new_cap = st.number_input("New Capacity MWel", format="%.2f")
            submitted = st.form_submit_button("Update")
            if submitted and project_name:
                project = db.projects.find_one({"name": project_name})
                result = db.productions.update_one(
                    {"project_id": project["_id"] if project else None},
                    {"$set": {"Capacity_MWel": new_cap}}
                )
                if result.modified_count:
                    st.success("Production updated successfully.")
                else:
                    st.warning("No matching production found or no change made.")
elif operation == "Delete":
    with st.form("delete_form"):
        if table == "countries":
            name = st.text_input("Country Name to Delete")
            submitted = st.form_submit_button("Delete")
            if submitted and name:
                result = db.countries.delete_one({"name": name})
                if result.deleted_count:
                    st.success("Country deleted successfully.")
                else:
                    st.warning("No matching country found.")

        elif table == "technologies":
            tech = st.text_input("Technology Name to Delete")
            submitted = st.form_submit_button("Delete")
            if submitted and tech:
                result = db.technologies.delete_one({"Technology": tech})
                if result.deleted_count:
                    st.success("Technology deleted successfully.")
                else:
                    st.warning("No matching technology found.")

        elif table == "projects":
            name = st.text_input("Project Name to Delete")
            submitted = st.form_submit_button("Delete")
            if submitted and name:
                result = db.projects.delete_one({"name": name})
                if result.deleted_count:
                    st.success("Project deleted successfully.")
                else:
                    st.warning("No matching project found.")

        elif table == "productions":
            project_name = st.text_input("Project Name to Delete Production")
            submitted = st.form_submit_button("Delete")
            if submitted and project_name:
                project = db.projects.find_one({"name": project_name})
                result = db.productions.delete_one({"project_id": project["_id"] if project else None})
                if result.deleted_count:
                    st.success("Production deleted successfully.")
                else:
                    st.warning("No matching production found.")

# ===== Sidebar =====
search_option = st.sidebar.selectbox(
    "Search by:",
    ("Project Name", "Technology", "Country", "Year Range", "Product", "Status")
)


# ====== Search by Technology ======
if search_option == "Technology":
    
    tech_name = st.sidebar.text_input("Enter technology name")
    if st.sidebar.button("Search"):
        if not tech_name:
            st.warning("\u26a0\ufe0f Please enter a technology name to search.")
        else:
            tech_doc = db.technologies.find_one({"Technology": tech_name})
            if tech_doc:
                tech_id = tech_doc["_id"]
                projects = db.projects.find({"technology_ids": tech_id})
                found_any = False
                for project in projects:
                    found_any = True
                    country_doc = db.countries.find_one({"_id": project.get("country_id")})
                    investment_doc = db.productions.find_one({"project_id": project["_id"]})
                    tech_names = [db.technologies.find_one({"_id": t})["Technology"] for t in project.get("technology_ids", [])]

                    with st.expander(f"📌 {project.get('name', 'N/A')}"):
                        st.markdown(f"""
                        **Status:** {project.get('status', 'N/A')}  
                        **Country:** {country_doc.get("name") if country_doc else "Unknown"}  
                        **Technologies:** {", ".join(tech_names)}  
                        **Product:** {project.get('product', 'N/A')}  
                        **Date Online:** {project.get('date_online', 'N/A')}  
                       
                        **Investment:** {investment_doc.get("announced_size") if investment_doc else "N/A"}  
                        **LOWE_CF:** {project.get('LOWE_CF', 'N/A')}  
                        **Location:** ({project.get('latitude', 'N/A')}, {project.get('longitude', 'N/A')})  
                        """)
                if not found_any:
                    st.warning("No projects found using this technology.")
            else:
                st.warning("❌ No technology found with this name.")

# ====== Search by Country ======
elif search_option == "Country":
    
    country_name = st.sidebar.text_input("Enter country name (e.g. Germany)").strip()

    if st.sidebar.button("Search"):
        if not country_name:
            st.warning("\u26a0\ufe0f Please enter a country name to search.")
        else:
            country_doc = db.countries.find_one({"name": {"$regex": f"^{country_name}$", "$options": "i"}})
            if country_doc:
                country_id = country_doc["_id"]
                projects = db.projects.find({"country_id": country_id})
                found_any = False
                for proj in projects:
                    found_any = True
                    tech_names = [db.technologies.find_one({"_id": t})["Technology"] for t in proj.get("technology_ids", [])]
                    productions = db.productions.find_one({"project_id": proj["_id"]})

                    with st.expander(f"📌 {proj.get('name', 'N/A')}"):
                        st.markdown(f"""
                        **Status:** {proj.get('status', 'N/A')}  
                        **Country:** {country_name}  
                        **Technologies:** {", ".join(tech_names)}  
                        **Product:** {proj.get('product', 'N/A')}  
                        **Date Online:** {proj.get('date_online', 'N/A')}  
                        
                        **productions:** {productions.get('announced_size') if productions else 'N/A'}  
                        **LOWE_CF:** {proj.get('LOWE_CF', 'N/A')}  
                        **Location:** ({proj.get('latitude', 'N/A')}, {proj.get('longitude', 'N/A')})  
                        """)
                if not found_any:
                    st.warning("❌ No projects found in this country.")
            else:
                st.warning("❌ Country not found.")

# ====== Search by Year Range ======
elif search_option == "Year Range":
    # st.subheader("Projects")
    from_year = st.sidebar.text_input("From Year")
    to_year = st.sidebar.text_input("To Year")

    if st.sidebar.button("Search"):
        if not from_year or not to_year:
            st.warning("\u26a0\ufe0f Please enter both start and end years.")
        else:
            try:
                from_year = int(from_year)
                to_year = int(to_year)

                if from_year > to_year:
                    st.warning("\u26a0\ufe0f The start year should be less than or equal to the end year.")
                else:
                    start_date = datetime(from_year, 1, 1)
                    end_date = datetime(to_year, 12, 31, 23, 59, 59)

                    projects = db.projects.find({
                        "date_online": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
                     })

                    found = False
                    for project in projects:
                        found = True
                        tech_names = [db.technologies.find_one({"_id": t})["Technology"] for t in project.get("technology_ids", [])]
                        productions = db.productions.find_one({"project_id": project["_id"]})

                        with st.expander(f"📌 {project.get('name', 'N/A')}"):
                            st.markdown(f"""
                            **Status:** {project.get('status', 'N/A')}  
                            **Country ID:** {project.get('country_id', 'N/A')}  
                            **Technologies:** {", ".join(tech_names)}  
                            **Product:** {project.get('product', 'N/A')}  
                            **Date Online:** {project.get('date_online', 'N/A')}  
                              
                            **Productions:** {productions.get('announced_size') if productions else 'N/A'}  
                            **LOWE_CF:** {project.get('LOWE_CF', 'N/A')}  
                            **Location:** ({project.get('latitude', 'N/A')}, {project.get('longitude', 'N/A')})  
                            """)
                    if not found:
                        st.warning("❌ No projects found in this year range.")
            except ValueError:
                st.error("❌ Please enter valid numbers for the years.")

# ====== Search by Product ======
elif search_option == "Product":
    # st.subheader("Projects")
    product_name = st.sidebar.text_input("Enter product name (e.g. Green Hydrogen, Ammonia, etc.)").strip()

    if st.sidebar.button("Search"):
        if not product_name:
            st.warning("\u26a0\ufe0f Please enter a product name to search.")
        else:
            projects = db.projects.find({"product": {"$regex": f"^{product_name}$", "$options": "i"}})
            found_any = False
            for project in projects:
                found_any = True
                country_doc = db.countries.find_one({"_id": project.get("country_id")})
                investment_doc = db.productions.find_one({"project_id": project["_id"]})
                tech_names = [db.technologies.find_one({"_id": t})["Technology"] for t in project.get("technology_ids", [])]

                with st.expander(f"📌 {project.get('name', 'N/A')}"):
                    st.markdown(f"""
                    **Status:** {project.get('status', 'N/A')}  
                    **Country:** {country_doc.get("name") if country_doc else "Unknown"}  
                    **Technologies:** {", ".join(tech_names)}  
                    **Product:** {project.get('product', 'N/A')}  
                    **Date Online:** {project.get('date_online', 'N/A')}  
                    
                    **productions:** {investment_doc.get('announced_size') if investment_doc else 'N/A'}  
                    **LOWE_CF:** {project.get('LOWE_CF', 'N/A')}  
                    **Location:** ({project.get('latitude', 'N/A')}, {project.get('longitude', 'N/A')})  
                    """)
            if not found_any:
                st.warning("❌ No projects found with this product.")

# ====== Search by Project Name ======
elif search_option == "Project Name":
    # st.subheader("Projects")
    search_term = st.sidebar.text_input("Enter project name keyword (e.g. hydrogen)").strip()

    if st.sidebar.button("Search"):
        if not search_term:
            st.warning("\u26a0\ufe0f Please enter a keyword to search.")
        else:
            projects = db.projects.find({"name": {"$regex": search_term, "$options": "i"}})
            found_any = False
            for project in projects:
                found_any = True
                country_doc = db.countries.find_one({"_id": project.get("country_id")})
                investment_doc = db.productions.find_one({"project_id": project["_id"]})
                tech_names = [db.technologies.find_one({"_id": t})["Technology"] for t in project.get("technology_ids", [])]

                with st.expander(f"📌 {project.get('name', 'N/A')}"):
                    st.markdown(f"""
                    **Status:** {project.get('status', 'N/A')}  
                    **Country:** {country_doc.get("name") if country_doc else "Unknown"}  
                    **Technologies:** {", ".join(tech_names)}  
                    **Product:** {project.get('product', 'N/A')}  
                    **Date Online:** {project.get('date_online', 'N/A')}  
                    
                    **productions:** {investment_doc.get('announced_size') if investment_doc else 'N/A'}  
                    **LOWE_CF:** {project.get('LOWE_CF', 'N/A')}  
                    **Location:** ({project.get('latitude', 'N/A')}, {project.get('longitude', 'N/A')})  
                    """)
            if not found_any:
                st.warning("❌ No projects found with this name.")



# ====== Search by Status ======
if search_option == "Status":
    # st.subheader("Projects")
    status_input = st.sidebar.text_input("Enter project status (e.g. Operational, Under Construction)").strip()

    if st.sidebar.button("Search"):
        if not status_input:
            st.warning("\u26a0\ufe0f Please enter a status to search.")
        else:
            projects = db.projects.find({"status": {"$regex": f"^{status_input}$", "$options": "i"}})
            found_any = False
            for project in projects:
                found_any = True
                country_doc = db.countries.find_one({"_id": project.get("country_id")})
                investment_doc = db.productions.find_one({"project_id": project["_id"]})
                tech_names = [db.technologies.find_one({"_id": t})["Technology"] for t in project.get("technology_ids", [])]

                with st.expander(f"📌 {project.get('name', 'N/A')}"):
                    st.markdown(f"""
                    **Status:** {project.get('status', 'N/A')}  
                    **Country:** {country_doc.get("name") if country_doc else "Unknown"}  
                    **Technologies:** {", ".join(tech_names)}  
                    **Product:** {project.get('product', 'N/A')}  
                    **Date Online:** {project.get('date_online', 'N/A')}  
                      
                    **productions:** {investment_doc.get('announced_size') if investment_doc else 'N/A'}  
                    **LOWE_CF:** {project.get('LOWE_CF', 'N/A')}  
                    **Location:** ({project.get('latitude', 'N/A')}, {project.get('longitude', 'N/A')})  
                    """)
            if not found_any:
                st.warning(f"❌ No projects found with the status '{status_input}'.")


# /////////////////////////////////////////
def get_top_technology():
    # استخدام pipeline لتحديد التكنولوجيا الأكثر استخدامًا
    pipeline = [
        {
            "$lookup": {
                "from": "projects",
                "localField": "project_id",
                "foreignField": "_id",
                "as": "project"
            }
        },
        { "$unwind": "$project" },
        { "$unwind": "$project.technology_ids" },
        {
            "$group": {
                "_id": "$project.technology_ids",  # تجميع باستخدام technology_id
                "project_count": { "$sum": 1 }  # حساب عدد المشاريع التي تستخدم هذه التكنولوجيا
            }
        },
        { "$sort": { "project_count": -1 } },  # ترتيب حسب عدد المشاريع
        { "$limit": 1 }  # أخذ التكنولوجيا الأكثر استخدامًا
    ]

    result = list(productions.aggregate(pipeline))
    if not result:
        return None, 0

    top_tech_id = result[0]['_id']
    project_count = result[0]['project_count']

    # جلب تفاصيل التكنولوجيا
    tech_details = technologies.find_one({"_id": top_tech_id})

    return tech_details, project_count


# واجهة Streamlit لعرض تفاصيل التكنولوجيا
if st.sidebar.button("Show Top Technology"):
    tech_details, project_count = get_top_technology()

    if not tech_details:
        st.warning("No technology found.")
    else:
        # عرض تفاصيل التكنولوجيا
        tech_name = tech_details.get("Technology", "Unknown Technology")
        tech_description = tech_details.get("Description", "No description available")
        tech_category = tech_details.get("Category", "Unknown Category")

        st.subheader(f"🔧 **Top Technology**: {tech_name}")
        st.markdown(f"**🧮 Number of Projects using this Technology:** {project_count}")
        st.markdown(f"**📖 Description:** {tech_description}")
        st.markdown(f"**📂 Category:** {tech_category}")

        # يمكنك إضافة تفاصيل أخرى إذا كانت موجودة في الـ "technologies" collection
        if 'OtherDetail' in tech_details:
            st.markdown(f"**⚙️ Other Details:** {tech_details['OtherDetail']}")

# /////////////////////////////////////////////////

def get_project_count_for_country(country_name):
    # البحث عن الدولة للحصول على ID
    country = db.countries.find_one({"name": country_name})
    if not country:
        return None, f"Country '{country_name}' not found."

    country_id = country["_id"]

    pipeline = [
        {
            "$lookup": {
                "from": "projects",
                "localField": "project_id",
                "foreignField": "_id",
                "as": "project"
            }
        },
        { "$unwind": "$project" },
        { "$match": { "project.country_id": country_id } },
        {
            "$group": {
                "_id": "$project.country_id",
                "project_count": { "$sum": 1 }
            }
        }
    ]

    result = list(db.productions.aggregate(pipeline))

    if not result:
        return 0, None  # الدولة موجودة بس مفيهاش مشاريع

    return result[0]["project_count"], None
st.sidebar.markdown("### 🌍 Project Count by Country")
country_input = st.sidebar.text_input("Enter country name")

if st.sidebar.button("Show Project Count"):
    if not country_input:
        st.warning("Please enter a country name.")
    else:
        project_count, error = get_project_count_for_country(country_input)

        if error:
            st.warning(error)
        else:
            st.subheader(f"📊 Project Count in {country_input.upper()}")
            st.markdown(f"🧮 **Total Projects:** {project_count}")
# /////////////////////////////////////////

st.sidebar.markdown("### 📊 Avg Capacity by Product")

if st.sidebar.button("Show Aggregation"):
    pipeline = [
        {
            "$lookup": {
                "from": "projects",
                "localField": "project_id",
                "foreignField": "_id",
                "as": "project"
            }
        },
        { "$unwind": "$project" },
        {
            "$group": {
                "_id": "$project.product",
                "avg_capacity": { "$avg": "$Capacity_MWel" },
                "count": { "$sum": 1 }
            }
        },
        { "$sort": { "avg_capacity": -1 } }
    ]

    result = list(db.productions.aggregate(pipeline))

    if result:
        st.subheader("🔍 Average Capacity (MWel) by Product")
        for item in result:
            st.markdown(f"""
            **Product:** {item['_id'] or 'Unknown'}  
            **Average Capacity:** {round(item['avg_capacity'], 2)} MWel  
            **Projects Count:** {item['count']}  
            """)
    else:
        st.warning("No data found for this aggregation.")

# ///////////////////////////


map_fn = Code("""
  function () {
    if (this.date_online) {
      var year = new Date(this.date_online).getFullYear();
      emit(year, this.name);
    }
  }
""")

reduce_fn = Code("""
  function (key, values) {
    return values;
  }
""")

db.command({
    "mapReduce": "projects",
    "map": map_fn,
    "reduce": reduce_fn,
    "out": "projects_by_year"
})



selected_year = st.sidebar.number_input("Enter Year (e.g. 2021)", step=1)

if st.sidebar.button("Show Projects for Year"):
    result = db.projects_by_year.find_one({"_id": int(selected_year)})
    projects = result["value"] if result else []

    if projects:
        st.subheader(f"📌 Projects in Year {int(selected_year)}")
        for proj in projects:
            st.markdown(f"- {proj}")
    else:
        st.warning("No projects found for this year.")
# ////////////////////////////////////////////



map_function = Code("""
  function () {
    if (this.product) {
      emit(this.product, 1);
    }
  }
""")

reduce_function = Code("""
  function (key, values) {
    return Array.sum(values);
  }
""")

# تنفيذ MapReduce باستخدام db.command
db.command({
    "mapReduce": "projects",
    "map": map_function,
    "reduce": reduce_function,
    "out": "product_project_count"
})

st.sidebar.markdown("### 🔍 Count Projects by Product (MapReduce)")

user_product = st.sidebar.text_input("Enter Product Name (e.g. H2, Ammonia, LOHC)")

if st.sidebar.button("Show Count"):
    if user_product:
        result = db.product_project_count.find_one({"_id": user_product})
        if result:
            st.success(f"🧮 Number of Projects for '{user_product}': {int(result['value'])}")
        else:
            st.warning(f"No projects found for product: '{user_product}'")
    else:
        st.warning("Please enter a product name.")

# /////////////////////////////


map_fn = Code("""
  function () {
    if (this.announced_size && this.project_id) {
      emit(this.project_id, this.announced_size);
    }
  }
""")

reduce_fn = Code("""
  function (key, values) {
    return Array.sum(values);
  }
""")

db.command({
    "mapReduce": "productions",
    "map": map_fn,
    "reduce": reduce_fn,
    "out": "investment_per_project"
})

# project_id → announced_size
project_investment = {
    doc["_id"]: doc["value"]
    for doc in db.investment_per_project.find()
}

# (year, product) → مجموع الإنتاج
year_product_totals = defaultdict(float)

for proj in db.projects.find():
    pid = proj["_id"]
    product = proj.get("product", "Unknown")
    date = proj.get("date_online")
    invest = project_investment.get(pid)

    if date and invest:
        year = date.year
        key = (year, product)
        try:
            cleaned_value = float(str(invest).replace("MW", "").replace("mw", "").replace("MWel", "").strip())
            year_product_totals[key] += cleaned_value
        except:
            continue


# حفظ النتائج في Collection جديدة
db.yearly_production_by_product.drop()
for (year, product), total in year_product_totals.items():
    db.yearly_production_by_product.insert_one({
        "year": year,
        "product": product,
        "total_production": total
    })

st.sidebar.markdown("### 📊 Yearly Total Production per Product")

if st.sidebar.button("📈 Show Production Summary"):
    import pandas as pd

    # 1. Load data from MongoDB
    data = []
    results = db.yearly_production_by_product.find()
    for doc in results:
        data.append({
            "Year": doc["year"],
            "Product": doc["product"],
            "Total Production": round(doc["total_production"], 2)
        })

    # 2. Create a pivot table: Year as rows, Product as columns
    if data:
        df = pd.DataFrame(data)
        pivot_df = df.pivot_table(
            index="Year", 
            columns="Product", 
            values="Total Production", 
            fill_value=0
        ).sort_index()

        # 3. Show table and chart
        st.subheader("📊 Total Annual Production by Product")
        st.dataframe(pivot_df)

        st.subheader("📈 Line Chart: Total Production Over Years")
        st.line_chart(pivot_df)
    else:
        st.warning("⚠️ No production data found.")


