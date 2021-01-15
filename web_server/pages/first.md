heading: Data Pipelines
sub_heading: What is a data pipeline?
published: 2021-01-03
author: Daniel Farrugia

# Your first data pipeline - A simplistic definition

In the most basic sense a data pipeline moves data from one storage location to another. A non-trivial example of one
such pipeline would be a service which continuously replicates a singe table between two relational databases. It is common
to find this type of pipeline in place when there is a need to isolate analytical workloads from the production environment.

In general, all non-trivial data pipelines will fulfill the following basic requirements:

 - The transfer of information from one location to another 
 - Run in a periodic and automated manner
 
 Often pipelines will apply some degree of transformation: 
 
 - Transformation from one data structure to another
 - Coercion of types
 - Data enrichment such as the addition of metadata 
 
## Hacker News  
 
For this tutorial we will use the [HackerNews API](https://hackernews.api-docs.io/v0/overview/introduction). For the
uninitiated HackerNews is an excellent community sourced technology news site. If your not a frequent reader I would
suggest becoming one. I've chosen this API as the data source for this series of tutorials because it is:

- **Open:** No auth is required and it is currently not rate-limited. 
- **Simple:** Whilst the website has a large amount of content the data model is easy to grasp.
- **High Traffic:** We will be required to construct well-architected solutions to many classic data engineering problems.
- **Interesting Dataset:** There is lots to build on as we progress.
- **It's Free:** As in beer.

#### HackerNews Data Model

The HackerNews API provides two main endpoints to access static data:

1. **[Items](https://github.com/HackerNews/API#items):** Everything is an item. Items are partitioned by the type field into posts, comments, polls and poll options. Items are identified by a unique [monotonically increasing](https://en.wikipedia.org/wiki/Monotonic_function) integer ID. 
2. **[Users](https://github.com/HackerNews/API#users):** User metadata. For this tutorial we will ignore this endpoint.

In addition to the static endpoints there are a number of endpoints which present live data. Again for the purposes of this tutorial the only live endpoint we will only concern ourselves with is: 

1. **[Max Item](https://github.com/HackerNews/API#max-item-id):** This endpoint returns the maximum item ID at the time of the request. 

## The task 
Lets take the above requirements for a data pipeline at face value and build a trivial data pipeline in Python. We are going to extract
items from [HackerNews](https://news.ycombinator.com/) and continuously save them to files on local disk space. We will thus satisfy
the above two requirements by: 

- **Transfering** data from HackerNews to your local HDD. 
- Executing the pipeline in an **automated** manner.

By leveraging the the ID column and max ID endpoint we can define upper and lower extraction bounds for each execution of our pipeline. Following the requests to the [max item](https://hacker-news.firebaseio.com/v0/maxitem.json) endpoint below:

    :::bash
    ➜  ~ echo "$(date)" " MAX ID: $( curl -s https://hacker-news.firebaseio.com/v0/maxitem.json\?print\=pretty)"
    Sun 10 Jan 2021 01:25:18 UTC  MAX ID: 25707367
    ➜  ~ echo "$(date)" " MAX ID: $( curl -s https://hacker-news.firebaseio.com/v0/maxitem.json\?print\=pretty)"
    Sun 10 Jan 2021 01:25:20 UTC  MAX ID: 25707375
    ➜  ~ echo "$(date)" " MAX ID: $( curl -s https://hacker-news.firebaseio.com/v0/maxitem.json\?print\=pretty)"
    Sun 10 Jan 2021 01:30:31 UTC  MAX ID: 25707441
   
If the pipeline executed every five minutes then the 1:30AM UTC execution would need to request items `25707376 <= ID <= 25707441` or 66 items.

### The Cold Start Problem -  What ID should the pipeline use to seed the initial run? 

There are several answers to this question but the best answer is - it depends! If your goal is to replicate the entire data source then the
best answer is:

    :::bash
    id = 1
 
 In theory our pipeline would execute starting at item one climbing incrementally until each and every item is extracted and the current max item is reached. If our goal is to continuously replicate from the present with no regard for historical data then we could use:
 
    :::bash
    id = MAX_ITEM_ID
    
### Batch Size
In both cases irrespective of the chosen seed value we have an issue. If `1` is chosen then the pipeline will execute continuously requesting circa 26 million items. There are many reasons to avoid this style of execution which can be explored at a later stage. If suffices to 
say that it is undesirable to allow a pipeline to execute with extremely large bounds. Likewise if the chosen seed is `id = MAX_ITEM_ID` then unless by chance an item with a higher ID is created between the max item ID request and the first new item request then the process 
will error (gracefully of course!) as `MAX_ITEM_ID + 1` does not exist yet. 

Both of these problems can be solved by batching your pipleine. Batching places a reasonable upper bounds on the number of items your pipeline can extract in any single execution.  

 
### Latency
In this sense latency will be a measure of the delay between the created time of most recent available item in your local storage and the current time. Latency is a core consideration of data pipeline design generally appearing at the top of requirements documents. Understanding the latency characteristics (it will be dynamic!) of your pipeline requires a nuanced understanding of each cost contributor:

- **Extraction Time:** How long does the it take to retrieve the data from a specific source? If your data source is an API then extraction time can be a considerable cost largely due to network costs and their relatively inflexibility compared to something like a database.
- **Processing Time:** Is inflight data transformation required before writing this data out to storage. For example *flattening* a highly nexted JSON response or *pivoting* a tabular data structure can be expensive operations with large data volumes that can contribute significantly to pipeline latency.
- **Write Time:** How long does it take to output the extracted data source to your chosen storage medium. Writing data from your pipeline's in memory data structure to an abritrary storage medium is simply another data transformation. The magnitude of difference between these two encodings and the efficiency at which the data can be transcoded will can contribute significantly to to this cost.  Much like the other cost categories, network cost can easily dominate this component by an order of magnitude.  For example, outputting JSON data line by line to a local file requires little transformation and zero network. Conversely writing the same JSON data to a *service* via an API will incur a large network penalty and see the data transcoded a number of times before arriving at its final destination.       
- **Data Velocity:** How fast is the data created? In the case of HackerNews we can see that on a typical Saturday new items are created at a rate of ~66 per 5 minutes (sample size one!) so one could say the velocity of HackerNews is 13 items a minute. If the flowrate of your pipeline does not exceed the velocity i.e our HackernNews pipeline must comfortably move greater then 13 items a minute from point A to point B. If a pipeline cannot meet this requirement then the data available for a consumer will inevitably lag as the latency increases. Thankfully data velocity is rarely constant and a well designed will easily accommodate for this variability and seamlessly recover from sudden bursts.
    
<!-- Comment inserted to render code *outside* the list -->
    :::python
    {{ save }}

### Appendix
 - *production*: The computing environment where operational systems run and from which they are exposed to customers. Due to
the operational dependency on production systems it is best practice to isolate them from human interaction.  
 - *service*: Generic catch-all term describing a program which performs some task without human interaction. Examples include a Web API which listening for new data, a message queue, a scheduled script which transforms new data
 - *Web API*: A process which listens for incoming web requests, performs some action and responds appropriately
 - *Scheduled script*: A standalone program that runs at regular intervals performing some automated task i.e moving new files from one location to another. 
 - *flattening*: 
 - *consumer*: Another service or a human which makes use of the incoming dataset