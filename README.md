# [findup] Find Duplicate files

This service is used to identify the duplicate files based on content hash from the given source folder.

This scans the entire source folder including all level sub-directories and identifies all duplicate file based on its content hash. 

There are three major parts to this service as 
1. Core engine :: that list and identifies all duplicate files.
2. WebUI :: is webserver that provides a browser based web UI client to perform user actions.
4. Database :: a persistanec storage of the data and statistics.
