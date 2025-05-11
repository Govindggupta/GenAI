# Query Routing
there are two types of routing 
1. Logical Routing
2. Semantic Routing

## Logical Routing

in logical routing, you find the best source of the data in the db and perform the RAG on that data.

for eg , there is data about nodejs , python , java and etc. <br>
user asks about the nodejs. <br>
so rather than finding the best answer in the whole db. <br>
we make diff collections for each language. <br>
now we route the llm to the best data source for the user query i.e, in this case nodejs 

so logical routing is nothing but when you logically route to something , it can be anything like db , file system , api etc. 

## Semantic Routing

In semantic routing , you've multiple prompts with you , now based on the user query you tell the llm to select the best and update accordingly. <br>
And then use that prompt for the llm to generate the answer.

eg: bolt and etc 

This is one part of semantic routing. please see about this more. 

From gpt : Semantic routing is a technique used to intelligently direct a user’s query or input to the most appropriate tool, agent, service, or function—based on the meaning (semantics) of the request, rather than keywords or hardcoded rules.



@ it has many implementations according to the use case.

link : https://app.eraser.io/workspace/nsZG1Pgs978nEmjT9Q3m