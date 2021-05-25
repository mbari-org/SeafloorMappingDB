### Original documents describing the system

```
From: Jenny Paduan
Subject: Re: SeafloorMappingDB schema
Date: May 20, 2021 at 4:38:49 PM PDT
To: Michael McCann
Cc: Karen Salamy Au
Reply-To: Jenny Paduan
```

Hi Mike and Karen,

Attached are the schema (as an Excel spreadsheet) and use cases (Word doc) that I put together last year as we began dreaming about this. I fully suspect as we go the need for other database fields or use cases might become apparent. 

As to the front end, both map-based and text-based interfaces will be useful. 

Examples I know of for map-based queries of bathymetric data utilize ship tracks to indicate the coverage, and include:

MGDS (at Lamont)
https://www.marine-geo.org/tools/new_search/search_map.php
I dislike how their prompts for things to search for are obscure and take getting used to. I also really dislike how their data sets are split out into so many parts it's hard to find everything and associate them with each other, but theirs is a different system.

The NCEI bathymetry viewer gives you a little more help than MGDS with the search prompts:
https://maps.ngdc.noaa.gov/viewers/bathymetry/
The "Search Bathymetric Surveys" button goes to a somewhat text-based search, which is veru useful if you already have a sense of what you're looking for. 

MGDS also has a feature that will construct grids from their archived data within a region you outline, which you can download as GRD or geoTiff files. I don't think we should go there, yet, but I can imagine someday others at MBARI might demand it. Part of the job for the MGDS folks is that they quality-control data before uploading into this part of their system, which makes the data available to anyone and everyone. It's useful, but I don't think I should promise this as a tool for our data (again, yet).
https://www.gmrt.org/GMRTMapTool/

I envision something that looks like the SamplesDB or ExpdDB web queries from Canyon Head for the text-based search. Having the clues for the search boxes is a bonus.

--Jenny

