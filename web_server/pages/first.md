heading: Data Pipelines
sub_heading: What is a data pipeline?
published: 2021-01-03
author: Daniel Farrugia


In the most basic sense a data pipeline moves data from one storage location to another. A non-trivial example of one
such pipeline would be a service which continuously replicates a singe table between two relational databases. It is common
to find this type of pipeline in place when there is a need to isolate analytical workloads from the production environment.

*Insert diagram here*

In general, all non-trivial data pipelines will fulfill the following requirements:

 - The transfer of information from one location to another 
 - Run in a periodic and automated manner
 
 Often pipelines will apply some degree of transformation: 
 
 - Manipulation from one data strcuture to another
 - Coercion of types
 - Data enrichment such as the addtiion of metadata
 
 
 
 
 
 https://hackernews.api-docs.io/v0/overview/introduction
 
Thus 

### Appendix
 - *production*: The computing environment where operational systems run and from which they are exposed to customers. Due to
the operational dependency on production systems it is best practice to isolate them from human interaction.  
 - *service*: Generic catch-all term describing a programs which perform some task without human interaction. Examples include:
 - *Web API*: A process which listens for incoming web requests, performs some action and responds appropriately
 - *Scheduled script*: A standalone program that runs at regular intervals performing some automated task i.e moving new files from one location to another. 