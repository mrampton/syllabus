# Intro

These are examples of problems that you may want to practice with. These problems are not graded.  Working with others on this is encouraged.



# Indexing Problems

Let's say we have 10,000 records and we create a secondary B+ tree index on the age attribute.  A pointer is 8 bytes, the age takes 4 bytes, a page has size 1000 bytes, we enforce a fill factor of 2/3, and ignoring other storage overheads, how many leaf nodes are in the tree?

        age takes 4 bytes, pointer is 8 bytes-
        A fill factor of 2/3 gives us only 666 bytes that can store data
        
        For directory pages we require N keys and N+1 pointers:
          
          N*(key size + pointer size) + pointer size < page size
          N(4 + 8) + 8 = 1000 

        Solving for N gives us 54 (key, pointer) pairs per directory page and a fanout of 55

        For leaf pages, we expect 666 / (4 + 8) = 55 entries per page

        With 10,000 records, we expect 10,000 / 55 = 181.8 = 182 (rounded up) data pages (leaf nodes) in the tree

        OK, what is the height of the tree?

          log_55 (182) = 1.29 = 2 (rounded up)

        So we need a root node, its' children, then the leaf nodes.  
        Accessing any tuple needs to read the root node, its child, and the correct leaf node, then 
        follow the pointer to the actual heap page containing the tuple.  
        That's 4 disk IOs.


Let's say my main memory has the following number of pages.  What is the expected number of disk accesses to access a given record?

* 10

        the root node is cached in memory, and a negligable fraction of the root's children are cached.
        So we can save one disk IO for the root being cached.  We expect 3 IOs.

* 100

        The root node and its children take up 1+55 pages in the cache and can be cached.  That saves 2 IO,
        for a total of 2 IOs (valid answer). It is also possible some fraction of the leaf nodes can be cached:
        186 leaf pages divided by 44 remaining pages in memory ~= 25% of the leaf nodes can be cached, so that saves us .25 IO.
        The cost is then 4 - 2 - 0.25 = 1.75 IOs.

* 1000

        All index pages can be cached in memory (1 root + 55 children + 182 leaf pages)
        Assuming the memory allocated to the index is not used for anything else, 
        it takes 1 IO to access the heap page containing the tuple. (Arguably, some of the
        remaining 762 pages could be used to cache the heap file, but we weren't given enough
        information to make an estimate about it).



Let's say age has 80 distinct values, and no index pages are cached in memory.  How many disk IOs (one per page) would I expect for a predicate of the form `age = CONSTANT`?

        there are 10,000 records, 80 distinct values, so we expect 125 tuples to match the predicate.
        Each tuple is a potentially a separate IO to a different heap page.

        the height is 2, the height is the _path length_ from root node to data node
        We need to read 3 total leaf pages (186 leaf pages / 80 = 3)
        So 2 IO to read the root and root's child, 3 for the data (leaf) pages, and 1 IO for each matching tuple.

        2 + 3 + 125 = 130 IOs



# Query Optimization Problems


## Simple Operator Case

Let's say we have the following statistics about the database with table R

        NCARD(R) = 1000
        ICARD(R) = 100
        # pages  = 100
        minmax(a1) = [0, 100]
        default selectivity = 0.1

Assuming no indexes, what is the cost in the number of pages to

1. Read all records in R?

        100 heap scan for all typse of accesses

1. Read all records where a1 = 10

        100

1. Read all records where a2 = 10

        100

Again, assuming no indexes, what is the estimated number of tuples where

1. TRUE

        1000

1. a1 = 10

        We can guess the selectivity of a1 from the index cardinality:
        1000 * 1/100 = 10

1. a2 = 10

        We have to guess using the default selectivity
        1000 * 0.1 = 100

1. a1 = 10 AND a2 = 10

        We can combine our guesses for a1 and a2:
        1000 * 1/100 * 0.1 = 1

Now, assuming we have a b+tree primary index on a1 with fanout 10 (question didn't originally specify fanout), what is the cost in number of pages to

1. Read all records in R?

        assuming fill factor = 1
        100
        
1. Read all records where a1 = 10?

        height = log_10 100 = 2
        3 pages

1. Read all records where a1 > 50?

        2 pages + 50% of pages = 2 + 50 = 52

1. Read all records where a2 = 10?

        index useless.
        100

Now assuming the b+tree was a secondary index on a1 with fanout 10 (previously not included in question), what is the cost in number of pages to

1. Read all records in R?

        assuming fill factor = 1
        100

1. Read all records where a1 = 10?

        3 pages + follow pointer to heap page = 4   

        A student points out that the cardinality of this predicate is 10.  In this case the cost is:
        3 pages + 10 tuples * 1 IO per tuple = 13

1. Read all records where a1 > 50?

        500 tuples match this predicate

        2 pages to get to leaf + 
        50 pages for the leaf pages + 
        (1 heap page access * 500 tuples) = 552

1. Read all records where a2 = 10?

        100


# Single Join query case

Let's say you have the following query

        SELECT *
        FROM  R, S
        WHERE R.bid = S.sid   

Where

        NCARD(R) = 1000
        NCARD(S) = 100
        ICARD(R.bid) = 1000
        ICARD(S.sid) = 10
        NPAGES(R) = 100
        NPAGES(S) = 10
        Primary B+Tree on R.bid
        Secondary B+Tree on S.sid  
        Fanout = 10 (previously not in question, sorry!)


What is the cost, in number of pages read, for executing the following joins, where the left relation is the outer, and the right relation is the inner?


1. R nested loops join S

        100 to read the outer
        1000 tuples in outer
        10 in inner
        100 + 1000 * 10 = 10100

1. R index nested loops join S

        100 to read outer
        1000 tuples in outer
        12 for index: index is height 1, so 2 IOs to leaf node + 1 to follow pointer * 10 tuples
          (matching tuples assumed to fit into one leaf page)
        100 + 1000 * 12 = 12100

1. S index nested loops join R

        10 to read outer
        100 tuples in outer
        3 for index: index has height 2, but primary index
        10 + 100 * 3 = 310

        
1. R merge sort join S

        assuming 3*(M+N)
        3 * (100 + 10) = 3 * 110 = 330 (pretty good for no index!)

What is

* the selectivity of the query?

        assuming not key-foreign key join
        selectivity = 1 / max(ICARD(R), ICARD(S)) = 1 / 1000 = 0.001

* the expected number of results of the above join?  

        1000 * 100 * 0.001

Now let's take memory into account.  Let's say we have `11` pages of memory, what is the cost, in number of pages 
_read from disk_ for the following?

1. R nested loops join S

        100 to read the outer
        1000 tuples in outer
        10 pages in inner
        but 10 pages can be cached in memory after scanning for the first outer tuple
        100 + 10 = 110
        
1. R index nested loops join S

        100 to read outer
        1000 tuples in outer
        10 index cost:
          first two levels of index can be cached
          (we assume they are cached in memory already)
          1 to follow pointer * 10 tuples  for index: 
          100 + 1000 * 10 = 10100

1. S index nested loops join R

        10 to read outer
        100 tuples in outer
        1 for index: first two levels can be cached
                    (we assume they are cached in memory already)
        10 + 100 * 1 = 110


1. R merge sort join S

        for our purposes, memory doesn't matter so much
        3 * (M+N) = 3 * 110 = 330

Let's say you have the following query, but with the same statistics and indexes as above

        SELECT *
        FROM R, S
        WHERE R.bid = S.sid AND R.bid = 10  (originally R.sid = S.sid, fixed to R.bid)

What would the Selinger optimizer pick as the best plan?


        The following are some options along with the best plan:

        assuming no cache
        predicate push down
        pipelined execution
        0.001 = Selectivity of (R.bid = 10 )
        1 tuple expected to match predicate
        Index nested loops join
        10 S tuples match on the join predicate


           INLJ
          /    \
        select  S
          |
          R

        3 IOs to get result tuple for R.bid = 10 predicate
        1 IO to read root node
        1 IO to read leaf page
        10 IOs to follow pointers for each of the 10 matching S tuples
        3 + 2 + 10 = 15 IOs total

        How about NLJ instead?


           NLJ
          /    \
        select  S
          |
          R

        3 IOs to get result tuple for R.bid = 10 predicate
        10 IOs to read all of S
        only scan S once
        3 + 1 * 10 = 13 IOs


        The second option is faster 




# Multi Join optimization

Suppose I run the following query

        SELECT *
        FROM R, S, T
        WHERE R.sid = S.sid AND S.sid = T.sid

And I have the following statistics about the relatons

        NCARD(R) = 100
        ICARD(R) = 100
        NCARD(S) = 1000
        ICARD(S) = 1000
        NCARD(T) = 10
        ICARD(T) = 10
        10 tuples per page  (originally not specified)

Suppose we have no other information, and we have not built any indices, and we only use nested loops join, work through the Selinger optimizer algorithm to

1. report the join orders the algorithm considers (the arguments to bestjoin())

        {R} 
        {S}
        {T}
        {R,S}  
        {R,T}
        {S,T}
        {R,S,T}

1. compute the selectivity of the query

        1 / max(100, 1000) = 0.001: R.sid = S.sid
        1 / max(1000, 10)  = 0.001: S.sid = T.sid
        0.001 * 0.001 = .000001

1. estimate the cardinality of the query result 

        100 * 1000 * 10 * 0.001 * 0.001 = 1

1. What is the minimum cost plan?

        ((T join R) join S)

        Recall NLJ is M + (M*N), so you want the M to be as small as possible.