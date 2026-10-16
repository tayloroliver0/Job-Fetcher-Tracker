import json , requests , sys , sqlite3, csv
from bs4 import BeautifulSoup

def main():
    pipeline = Pipeline()
    while True:
        userselect = input("\n1. Fetch new listings \n"
        "2. Browse jobs \n"
        "3. Application Tracker \n" 
        "4. Exit Program \n\n"
        "Choice: "
        )

        if userselect == "1":
                while True: 
                    normjobs, fails = normfetch_jobs()
                    pipeline.store_jobs(normjobs)
                    if fails:
                        for name, error in fails:
                            print(f"\033[1;31mERROR: {name}: {error}\033[0m")
                        answer = input("Retry? (y/n): ")
                        if answer == "y":
                            continue  
                        else:
                            break
                    if not fails:
                        break
        elif userselect == "2":
            category = input("Category? ")
            keyword = input("Keyword? ")
            if category == "":
                category = None
            if keyword == "":
                keyword = None
            jobs = pipeline.list_jobs(category=category, keyword=keyword)
            for job in jobs:
                print(job)
            shortdes = input("\nExport shortlist to CSV? (y/n): ")
            if shortdes == "y":
                filepath = input("Save As (.csv): ")
                export_shortlist(jobs=jobs,filepath=filepath)              
        elif userselect == "3":
            trackjobid = input("Job ID to track: ")
            while True:
                trackjob = input("\n1. Add Job to Tracker \n"
                "2. Update Job Status \n"
                "3. Add Note \n"
                "4. Change Job ID \n"
                "5. Exit menu \n\n"
                "Choice: ")
                if trackjob == "1":
                    pipeline.add_application(trackjobid=trackjobid)
                elif trackjob == "2":
                    status = input("Job Status: ")
                    pipeline.adj_status(trackjobid=trackjobid, status=status)
                elif trackjob == "3":
                    note = input("Note: ")
                    pipeline.add_note(trackjobid=trackjobid, note=note)
                elif trackjob == "4":
                    trackjobid = input("Job ID to track: ")
                elif trackjob == "5":
                    break
        elif userselect == "4":
            sys.exit()

class Job:
    def __init__(self,id=None, title=None, companyname=None, salary=None, jobtype=None, requiredlocation=None, category=None, description=None):
        self.id = id
        self.title = title
        self.companyname = companyname
        self.salary = salary
        self.jobtype = jobtype
        self.requiredlocation = requiredlocation
        self.category = category
        self.description = description
    def __str__(self):
        return (f"\nJob ID: {self.id} \n"
    f"Title: {self.title} \n"
    f"Company Name: {self.companyname} \n" 
    f"Salary: {self.salary} \n" 
    f"Job Type: {self.jobtype} \n" 
    f"Required Location: {self.requiredlocation} \n" 
    f"Category: {self.category} \n" 
    f"Description: {self.description} \n\n")
    def as_tuple(self):
        return(self.id,self.title,self.companyname,self.salary,self.jobtype,self.requiredlocation,self.category,self.description)


class Pipeline:
    def __init__(self, dbpath="jt.db"):
        self.con = sqlite3.connect(dbpath)
        self.cur = self.con.cursor()
        self.cur.execute("PRAGMA foreign_keys = ON")
        self.cur.execute("CREATE TABLE IF NOT EXISTS Jobs (Id INTEGER UNIQUE, Title, Company_Name, Salary, Job_Type, Required_Candidate_Location, Category, Description)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS Applications (Application_ID INTEGER PRIMARY KEY AUTOINCREMENT, Job_ID INTEGER UNIQUE REFERENCES Jobs(Id), Status, Notes)")

    def store_jobs(self, jobs):
        jobs = clean_description(jobs=jobs)
        filledtable = self.cur.executemany("INSERT INTO Jobs VALUES(:id, :title, :company_name, :salary, :job_type, :candidate_required_location, :category, :description) ON CONFLICT (Id) DO NOTHING",jobs)
        self.con.commit()

    def list_jobs(self, category=None, keyword=None):
        conditions = []
        values = []
        if category is not None:
            conditions.append("Category = ?")
            values.append(category)
    
        if keyword is not None:
            conditions.append("(Title LIKE ? OR Company_Name LIKE ? OR Salary LIKE ? OR Job_Type LIKE ? OR  Required_Candidate_Location LIKE ? OR Category LIKE ? OR Description LIKE ?)")
            n = 7
            while n > 0:
                values.append(f"%{keyword}%")
                n = n - 1

        if conditions:
            conditions = " AND ".join(conditions)
            query = f"SELECT * FROM Jobs WHERE {conditions}"
        else:
            query = "SELECT * FROM Jobs"
            values = ""
        
        self.cur.execute(query,values)
        jobs = self.cur.fetchall()
        filtjob = []
        for job in jobs:
            filtjob.append(Job(*job))
        return filtjob
    def add_application(self, trackjobid):
        try:
            self.cur.execute("INSERT INTO Applications(Job_ID) VALUES(?)", (trackjobid,))
            self.con.commit()
        except sqlite3.IntegrityError as e:
            if "UNIQUE" in str(e):
                print("\n\033[1;31mERROR: THIS JOB ID ALREADY EXISTS IN YOUR TRACKER\033[0m")
            elif "FOREIGN KEY" in str(e):
                print("\n\033[1;31mERROR: THIS JOB ID DOES NOT EXIST. CHECK THE ID FROM BROWSE\033[0m")
            else:
                raise
    def adj_status(self, trackjobid, status):
            self.cur.execute("UPDATE Applications SET Status = ? WHERE Job_ID = ?", (status,trackjobid))
            if self.cur.rowcount == 0:
                print("\n\033[1;31mERROR: THIS JOB ID DOES NOT EXIST. CHECK THE ID FROM BROWSE\033[0m")
            else:self.con.commit()
    def add_note(self, trackjobid, note):
            self.cur.execute("UPDATE Applications SET Notes = ? WHERE Job_ID = ?", (note,trackjobid))
            if self.cur.rowcount == 0:
                print("\n\033[1;31mERROR: THIS JOB ID DOES NOT EXIST IN YOUR TRACKER\033[0m")
            else:
                self.con.commit()

def fetch_jobs():
    try:
        r =requests.get("https://remotive.com/api/remote-jobs?search=", timeout=10)
        r.raise_for_status()
        o = r.json()
        return o["jobs"]
    except requests.ConnectionError:
        print("\n\033[1;31mERROR: UNABLE TO CONNECT TO SERVER\033[0m")
        raise

def fetch_remoteok_jobs():
    try:
        r = requests.get("https://remoteok.com/api", timeout=10)
        r.raise_for_status()
        o = r.json()
        return o[1:]
    except requests.ConnectionError:
        print("\n\033[1;31mERROR: UNABLE TO CONNECT TO SERVER\033[0m")
        raise

def clean_salary(min, max):
    if max == 0:
        return "Not Listed"
    else:
        return f"${min} - ${max}"

def normfetch_jobs():
    normjobs = []
    fails = []
    try:
        remotive_jobs = fetch_jobs()
        for job in remotive_jobs:
            normjob = {
                "id": job["id"],
                "title": job["title"],
                "company_name": job["company_name"],
                "salary": job["salary"],
                "job_type": job["job_type"],
                "candidate_required_location": job["candidate_required_location"],
                "category": job["category"],
                "description": job["description"]
            }
            normjobs.append(normjob)
    except requests.RequestException as e :
        fails.append(("remotive", e))
    try:
        remoteok_jobs = fetch_remoteok_jobs()
        for job in remoteok_jobs:
            normjob = {
                "id": job["id"],
                "title": job["position"],
                "company_name": job["company"],
                "salary": clean_salary(min=job["salary_min"], max=job["salary_max"]),
                "job_type": None,
                "candidate_required_location": job["location"],
                "category": None,
                "description": job["description"]
            }
            normjobs.append(normjob)
    except requests.RequestException as e:
        fails.append(("remoteok", e))
    return normjobs, fails


#Cleans Description for each Job.
def clean_description(jobs):
    for job in jobs:
        dirtydescription = job["description"]
        soup = BeautifulSoup(dirtydescription, 'html.parser')
        description = soup.get_text()
        job["description"] = description
    return jobs
def export_shortlist(jobs,filepath):
    with open(filepath, "w", newline='') as csvfile:
        writer = csv.writer(csvfile)                     
        writer.writerow(['Job_ID', 'Title', 'Company_Name', 'Salary', 'Job_Type', 'Required_Candidate_Location', 'Category', 'Description'])
        for job in jobs:
            writer.writerow(job.as_tuple())

if __name__ == "__main__":
    main()