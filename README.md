# PyDBL
### In-memory Database with object grammar

*PyDBL is an in-memory persistent and non-persistent database which supports SQL and NoSQL query types*
<br/>


### Query Type Support:
#### SQL
`IMPORT`, `SELECT`, `UPDATE`, `DELETE`, `INDEX`

#### NoSQL
`HSET`, `HGET`
<br/>


### The query engine is divided in two sections:
* Query Compiler
* Query Engine


#### Query Compiler
The Query Compiler breaks down object query into `Intermediate Representation (IR)`. This IR is fed to the Query Engine for further database related operations. The Compiler Query breaks down the query as follows:
1. Lexing
2. Parsing
3. Flattening
4. IR Formation


#### Query Engine
The Query Engine plays a significant role in query processing as a backend service to the compiler. 
1. The IR fed by the db compiler segregates the query into SQL and NoSQL types. 
2. Further SQL queries are optimized using either:
   * Batch processing where `Local Value Numbering` is used to remove repetitve queries.
   * `Indexing` on views using `B+ Trees` to support quick retrival.

<br/>
<br/>

### Syntax

We have introduced a novel way of writing conditions *The WHERE Clause* giving opportunities to include optimized nesting inside queries increasing readability and feel like dynamic-typed queries. 

#### Conditions 
*Writing the WHERE Clause* 
```python
condition1 = {">" : ("Baths", 3)}
```
<u>
Object disclosing key as operator: {<, >, <=, >=, ==, !=} comparing left tuple value(column name) with right (value) i.e . Baths > 3
</u>

*Combining multiple queries*
*Using the query variable `condition` from above*
```python
condition1 = {">" : ("Baths", 3)}
condition2 = {"==" : ("Bedroom", "large")}
condition3 = {"or" : (condition1, condition2)}
```
<u>
Object disclosing key as boolean condition operator {and, or} comparing left tuple condition with right condition i.e. condition1 or condition2
</u>