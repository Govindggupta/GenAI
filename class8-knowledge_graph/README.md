# knowledge_graph

this is used to generate the relationship between the entities / nodes in the form of a graph and hence called as knowledge graph.

eg : govind -- likes --> sweets 
so here govind and sweets are nodes and like is edge between them which shows relationship between nodes . 

like mysql run on sql language , this runs on cypherql i.e, cypherql is used to talk with the graphDB. 

example of the cypherQL : <br>
    CREATE ( c: Person{name : 'Govind', age : 25, gender : 'Male'} ) return c <br>
    : so this create a node of perosn with name govind and other attributes


## Indexing 

now indexing nodes can be done this ways : <br>
1. raw  <br>
2. langchain <br>
3. mem <br>

### 1. raw 
in this on the basis of the data , you create the entities by the ai and then directly index them by adding them into the command : <br>
entities = [ ] , for entity in entities : MERGE (e:Entity{name : entity.name}) return e <br>

so by this we are adding the entities into the db and similarly relationships can be done 

### 2. langchain 
