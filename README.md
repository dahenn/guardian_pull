# guardian_pull

See the project <a href="http://danneh.co/police-killings.html" target="_blank">here</a>.

## Project Motivation

I originally discovered this dataset through FiveThirtyEight's reporting on <a href="http://fivethirtyeight.com/features/where-police-have-killed-americans-in-2015/" target="_blank">"Where Police Have Killed Americans In 2015"</a>. This led me to discover The Guardian's ongoing project called <a href="http://www.theguardian.com/us-news/ng-interactive/2015/jun/01/the-counted-police-killings-us-database" target="_blank">"The Counted"</a>. FiveThirtyEight took the data and expanded the analysis a bit, using census tract information to give statistics regarding average income for the areas in which people were killed. The Guardian's webpage did less analysis, but continuously updates their data. I thought that the full up-to-date data set could provide some interesting insights, especially regarding the demographics of those killed and the circumstances under which they were killed.

Further, while this is a rather gruesome subject, it is one that has become a national focus. So, the prospect of some additional insight becomes more alluring.

## Pulling

Relevant Files:
<ul>
<li>pull_2015.py</li>
<li>pull_2016.py</li>
<li>chromedriver.exe</li>
</ul>

The Guardian's webpage seemed to be prime for some simple webscraping. As it turned out, it actually took some not-so-simple webscraping. The full information for each event can only be seen when the element is active. To make that possible, I used the Selenium WebDriver package for Python. This allowed me to automatically click in and out of each listing, and gathering data along the way. This made the webscraping process take a significant time, as there is difficulty with load times and the loading of individual elements.

## Storing and Processing

Relevant Files:
<ul>
<li>police_killings.sqlite</li>
<li>load_location.py</li>
<li>chart_analyze.py</li>
<li>pop_race.csv</li>
</ul>

All of the data was stored in a SQL database using SQLite and Python. I process the data in three steps. First, I wanted to sort the data by date and add a date index field. I originally wanted this because I planned on mapping the data along with a timeline in order to see the deaths across time. I haven't yet implemented that on the front end, but the data is available in order to make it possible. The second step of processing was to map addresses to latitudes and longitudes. I did this using the Google Maps API, and wrote the results out to a json file. Finally, I did an analysis to determine the frequency of deaths based on U.S. demographics and whether or not the victim was armed. For this, I used the pandas package for Python, grouping and reshaping the data in different ways.

## Mapping and Visualizing

Relevant Files:
<ul>
<li>event_points.json</li>
<li>states.json</li>
<li>map-zoom.html</li>
<li>pop_race.csv</li>
</ul>

I did two main projects using d3.js. First was the map, which is zoomable and color-coded based on race and status of the victim. I also created a stacked bar chart to display an aggregated view of the data.

## Possible Extensions

There is much room for expansion on this project. Using census tract information, as FiveThirtyEight did, would provide some very interesting information that could open up possibilities for regression analyses, or just generally opening up other socioeconomic factors. There are also extensions within the current data, such as the timeline addition to the map, or other ways of slicing summaries. 
