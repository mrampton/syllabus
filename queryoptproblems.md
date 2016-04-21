# Intro

The following are examples of problems that you may want to practice with.  I'll supply answers to a subset of the problems at a later date, so you can work out the rest.

These problems are not graded.  Working with others on this is encouraged.

NOTE: I manually split this into just the problems, and the [solutions in a separate file](./queryoptproblems-solutions.md); If you found I removed a critical part of the question, please let me know.


# Indexing Problems

1. Let's say we have 10,000 records and we create a secondary B+ tree index on the age attribute.  A pointer is 8 bytes, the age takes 4 bytes, a page has size 1000 bytes, we enforce a fill factor of 2/3, and ignoring other storage overheads, how many leaf nodes are in the tree? What is the height of the tree? How many disk accesses does it take to read a tuple matching a given key (equality search?)

1. Let's say my main memory has the following number of pages.  What is the expected number of disk accesses to access a given record?

    a. * 10
    b. * 100
    c. * 1000

1. Let's say age has 80 distinct values, and no index pages are cached in memory.  How many disk IOs (one per page) would I expect for a predicate of the form `age = CONSTANT`?


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

1. Read all records where a1 = 10

1. Read all records where a2 = 10

Again, assuming no indexes, what is the estimated number of tuples where

1. TRUE

1. a1 = 10

1. a2 = 10

1. a1 = 10 AND a2 = 10

Now, assuming we have a b+tree primary index on a1 with fanout 10 (question didn't originally specify fanout), what is the cost in number of pages to

1. Read all records in R?
        
1. Read all records where a1 = 10?

1. Read all records where a1 > 50?

1. Read all records where a2 = 10?

Now assuming the b+tree was a secondary index on a1 with fanout 10, what is the cost in number of pages to

1. Read all records in R?

1. Read all records where a1 = 10?

1. Read all records where a1 > 50?

1. Read all records where a2 = 10?


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

1. R index nested loops join S

1. S index nested loops join R
        
1. R merge sort join S


What is

* the selectivity of the query?
* the expected number of results of the above join?  

Now let's take memory into account.  Let's say we have `11` pages of memory, what is the cost, in number of pages 
_read from disk_ for the following?

1. R nested loops join S
        
1. R index nested loops join S

1. S index nested loops join R

1. R merge sort join S

Let's say you have the following query, but with the same statistics and indexes as above

        SELECT *
        FROM R, S
        WHERE R.bid = S.sid AND R.bid = 10  (originally R.sid = S.sid, fixed to R.bid)

What would the estimated cost be for the following index nested loops plan?


        The following are some options along with the plan:

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



What about an nested loops join?


           NLJ
          /    \
        select  S
          |
          R


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

1. compute the selectivity of the query

        1 / max(100, 1000) = 0.001: R.sid = S.sid
        1 / max(1000, 10)  = 0.001: S.sid = T.sid
        0.001 * 0.001 = .000001

1. estimate the cardinality of the query result 

        100 * 1000 * 10 * 0.001 * 0.001 = 1

1. Suggest a the minimum cost plan

        ((T join R) join S)

        Recall NLJ is M + (M*N), so you want the M to be as small as possible.
