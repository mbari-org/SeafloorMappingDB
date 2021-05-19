# Seafloor Mapping Database

*Make MBARI seafloor mapping datasets more accessible and useful*

## Text from the proposal

MBARI has now conducted hundreds of Mapping AUV missions and several dozen 
low altitude survey ROV dives. Much of the resulting data have value to others 
in the MBARI community, but the survey data and data products are only 
accessible to those with both knowledge of where the data are stored, how they 
are organized, and how to run the software used to process the data in maps, 
images, and GIS objects. In order to make the Mapping AUV and LASS survey data 
more accessible, we propose to capture metadata such as geographic location and 
server storage paths in a relational database with a queryable web interface. 
The envisioned system will utilize the same approach and open-source software 
tools as the MBARI STOQS database for water-column data. This system can be 
developed without changing the current file-based structure on the 
SeafloorMapping share or impacting the work-flow for processing the sensor 
data. The data will remain as files on the SeafloorMapping share on Titan. 
Because the Titan server is web-accessible, metadata and data products can be 
mined for populating the database and viewed through the query interface.


