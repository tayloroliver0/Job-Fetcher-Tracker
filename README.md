# Job Fetcher and Application Tracker
Oliver Taylor
GitHub: https://github.com/tayloroliver0
edX: tayloroliver0
Beysour, Lebanon
09/26/2026
#### Video Demo: https://youtu.be/uDvNYVL4EAU

#### Description:


This project is a job fetcher and application tracker. Interacting with the code allows users to instantly fetch job listings, sort through them based on certain criteria and export filtered searches to CSV. The code also creates an application tracker for the user wherein they can instruct the code to add jobs and adjust their status and other features.


## Features
- Jobs fetched directly from Remotive using its built in API.
- A table of fetched jobs is automatically created on the first fetch, and updated duplicate free on any subsequent fetches.
- Jobs can be filtered through and browsed with the option to export filtered shortlists as CSV.
- An application tracker is automatically created upon addition of the first job to the tracker.
- Application tracker allows addition of jobs, addition of custom notes, and updating status of application.


## Files
- project.py (the main program)
- test_project.py (the file that tests the main program)
- requirements.txt (the file containing all the project dependencies)
- README.md (the file you are reading which contains important information about how other files in the directory work and are to be used)


### project.py
- The project file itself which calls a main function where a CLI is displayed.
- When option 1 is chosen (Fetch new listings), a new Pipeline object is created wherein a table for the fetched jobs and a table for the application tracker are created. The store_jobs method then calls upon the fetch_jobs function to intake jobs from the Remotive API, parse it and format it as a list of job dictionaries and pass it to store_jobs where it calls the clean_description function passing the raw list as a parameter and cleaning the description (originally formatted in HTML). The updated list of job dictionaries (now with clean descriptions) is given to store_jobs where non-duplicate jobs are appended to the table.
- When option 2 is selected (Browse Jobs), the user is then prompted for desired filters such as Keywords and Category. These values are then passed in as optional parameters to the list_jobs method in the Pipeline class, where depending on the passed in parameters, a SQL string is created and the relevant listings are pulled from the jobs table. The jobs are then looped through, and a Job object is created for each, wherein a str method returns the jobs characteristics as a string which is then stored in a filtered jobs list and displayed neatly in the CLI upon completion. An option to export the filtered jobs is then presented where if called, the user is prompted for a filepath then the export_shortlist function is called taking the filtered jobs and the filepath name as parameters and a CSV file is created with relevant headers and the jobs data.
- When option 3 is selected (Application Tracker), the user is immediately prompted for the ID of the job they desire to work with and then prompted for their choice of either adding a job to the tracker, updating an existing job's status, or attaching a note to the job in the tracker. If the user opts to add the job to the tracker, the add_application method in Pipeline is called, and the job id is checked against the table, (raising an error message if it already exists) then inserted into the application tracker. The same process of inserting the given value into a given job's table is repeated with the adj_status and add_note method according to the user's selection.




### test_project.py
- The file which tests the code's three top level functions using injected data, temporary file paths exclusive to the test's instance, and a custom class, as well as importing a class from the project file.
- The file defines test data as variables including a test job and a test JSON.
- The file tests the export shortlist function by creating a temporary filepath using pathlib exclusive to the instance of the test, then using testjob — a list of Job objects built at the top of the file via the imported Job class, it confirms the creation of a CSV and its containment of the complete test data in the correct format.
- The file also tests the clean description function by injecting test data and testing its output cleans the html in the description of the test data.
- The file then tests the fetch jobs function by defining a mock response class containing a static method which holds test data as JSON. The test then replaces requests.get itself with a fake function monkeypatch, so when the fetch job runs (and eventually calls requests.get(...) with its own hardcoded URL), it receives the MockResponse instead of a real network reply.

### requirements.txt
- Contains pip dependencies, used to install dependencies in one line.


## Design decisions


### Why SQLite over a flat file
- I needed data persistence , but also needed to query and filter that data and update specific rows later. A flat file can store data, but has no built-in way to query and filter that data without having to read the whole file and build custom logic for each operation myself. SQLite has all of the above built in.
### Why two tables instead of one
- I originally contemplated having the Application tracker as columns in the jobs table. I ultimately decided to make them separate tables because if status/notes lived as columns on Jobs directly, every unapplied job would need placeholder values in columns that don't apply to it.
### Why clean_description takes jobs as a parameter
- Originally the function called fetch_jobs() internally, but while building my test I realized this would trigger a real network request every time. I therefore decided to have it take Jobs as a parameter in order to have control of the data it is fed for testing purposes without triggering a real network request
### What I cut, and why
- I initially planned on having a Scorer class and status_history function. Both were part of the original design (scoring job fit, logging every status change over time), and were dropped after I decided status history was not essential and just allowing the user to overwrite it as needed was not an issue. I also dropped scoring because I felt it was not necessary for v1.


## Setup
Install all dependencies using:
   "pip install -r requirements.txt"
