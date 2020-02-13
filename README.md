# The Talent Aquisition Team dashboard

## Views
|Page|URL|Access|Purpose in life|
|---|---|---|---|
|Live postings|/livePostings|Members, TA team|To have only *live* postings populated in the dropdowns & avoid all ~~archived~~ postings|
|Archived postings|/archivedPostings|Members, TA team|To have only *archived* postings populated in the dropdowns & avoid all ~~live~~ postings.|
|Recruiter filter : Live postings|/recruiterLivePostings|TA team|Very similar to /livePostings. But has filter of Recruiter on the top to filter out our choice of recruiters in the report.|
|Recruiter filter : Archived postings|/recruiterArchivedPostings|TA team|Very similar to /archivedPostings. But has filter of Recruiter on the top to filter out our choice of recruiters in the report.|
|Team reports|/team|TA team|TA team reports for internal assessment.|
|User|/modifyUsers|Admin|A user management module for the admin.|
|Upload|/upload|Admin|Used to feed csv files downloaded from Lever for the dashboard to assimilate & render reports.|

## Logic
### Tables & funnels
All tables & funnels filter (as in /livePostings, /archivedPostings, /recruiterLivePostings and /recruiterArchivedPostings ) candidates based on a common logic.
#### Logic for calculating the table in /livePostings
* "Posting Archive Status" is TRUE/FALSE. It doesn't shows whether a Posting is archived or not. Instead it tells about the "Profile Archive Status". Lever uses the names in weird ways.

Origin > Referals are hard to find.
Atleast just by referring the column "Origin" it can't be determined.
Look for status in Referred, Is Social Referral or Is Employee Referral

#### Removing Postings with Internal (I)

### Upload & Store
* Two unadulterated .csv files are required to be fed in the app via */upload* module. 
*Note: Even opening the .csv & then saving alters the file contents.*
* Let's call the big & small CSVs as BigFile & SmallFile respectively.
* Store .... blah ... blah ...
	#### BigFile 
	* **Removing duplicates** : Removing duplicate candidate entries .... blah ... blah ...
	* Detemining posting created date:
	* Determining Actual Posting Owner Name:
	#### SmallFile
	* It's sole purpose to decide Posting's Open or Closed status.







## Team Reports
There are three tabs:
|Tab|Description|
|---|---|
|New applicant|Count of candidates still in *New Applicant* stage displayed recruiter wise in yearly calender|
|Archived|Days elapsed on candidates from *Application* till they are *Archived*, filtered recruiter wise.|
|Offered|Days elapsed on candidates from *Application* till they are been *Offered*, filtered recruiter wise.|

They all are triggered to render the reports upon hitting the **GO** button. All of them are governed by origin & Date filters which may be altered to get respective cuts.
