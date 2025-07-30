--Creating a pdf chat bot
--Pre-req pdf file(s) available in blob storage
-- blob storage connected with the snowflake instance

use role sysadmin;


--create a place to store this data
CREATE DATABASE IF NOT EXISTS cortex_search_tutorial_db;

--create a compute node we can use in this lab
CREATE OR REPLACE WAREHOUSE cortex_search_tutorial_wh WITH
     WAREHOUSE_SIZE='X-SMALL'
     AUTO_SUSPEND = 120
     AUTO_RESUME = TRUE
     INITIALLY_SUSPENDED=TRUE;

 USE WAREHOUSE cortex_search_tutorial_wh;

--NOTE THIS IS NOT NEEDED IF YOU HAVE SETUP A STAGE PRIOR
--Give it a name you will remember
 
 --For the purposes of this lab, I'm going to use an internal stage
 -- this just means the s3 bucket is hosted in my  snowflake AWS account vs my own aws account
 -- note enabling the directory opens the door for easier cdc as new files are added.. HIGHLY recommend

 /*
 CREATE STAGE if not exists cortex_search_tutorial_db.public.doc_repo
    DIRECTORY = (ENABLE = TRUE)
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');
*/

--let's verify connectivity to the stage
ls @doc_repo;

--sidenote - you can give it a dir to filter which files we are looking at..
ls @doc_repo/docx;

/*
CHECKPOINT - We now have a place to store insights (the db)
We can now access files we will need for the lab (from the stage)
We have a compute node we can use to execute jobs (the warehouse)
*/

--Let's start parsing the files

--create a table to store the raw text
CREATE TABLE if not exists cortex_search_tutorial_db.public.raw_text AS
SELECT
    RELATIVE_PATH,
    TO_VARCHAR (
        SNOWFLAKE.CORTEX.PARSE_DOCUMENT (
            '@doc_repo', --your stage name here!!!
            RELATIVE_PATH,
            {'mode': 'LAYOUT'} ):content
        ) AS EXTRACTED_LAYOUT
FROM
    DIRECTORY('@cortex_search_tutorial_db.public.doc_repo') --your stage name here!!!
WHERE
    RELATIVE_PATH LIKE '%.pdf'; --filter on pdf!!!

--should we get the docx files as well?
--I dont want to replace the table... so let's just insert this time
    insert into cortex_search_tutorial_db.public.raw_text 
SELECT
    RELATIVE_PATH,
    TO_VARCHAR (
        SNOWFLAKE.CORTEX.PARSE_DOCUMENT (
            '@doc_repo', --your stage name here!!!
            RELATIVE_PATH,
            {'mode': 'LAYOUT'} ):content
        ) AS EXTRACTED_LAYOUT
FROM
    DIRECTORY('@cortex_search_tutorial_db.public.doc_repo') --your stage name here!!!
WHERE
    RELATIVE_PATH LIKE '%.docx'; --filter on docx!!!
    
--sample the data
Select * from raw_text;


-- Alright, well. EXTRACTED_LAYOUT column is hosting a LOT of text... We'd be best served chunking this.
CREATE TABLE if not exists cortex_search_tutorial_db.public.doc_chunks AS
SELECT
    relative_path,
    BUILD_SCOPED_FILE_URL(@doc_repo, relative_path) AS file_url,--update the @stage_name here for your stage
    CONCAT(relative_path, ': ', c.value::TEXT) AS chunk,
    'English' AS language
FROM
    cortex_search_tutorial_db.public.raw_text,
    LATERAL FLATTEN(SNOWFLAKE.CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER(
        EXTRACTED_LAYOUT,
        'markdown',
        2000, -- chunks of 2000 characters
        300 -- 300 character overlap
    )) c;

--sample the data
Select * from doc_chunks limit 100;
select distinct relative_path from doc_chunks;
--ok, this looks much better in chunks


/*
CHECKPOINT - We now have prepared the files into chunks for the cortex search service
Let's build the service!
*/

CREATE OR REPLACE CORTEX SEARCH SERVICE cortex_search_tutorial_db.public.document_search_service
    ON chunk
    ATTRIBUTES language
    WAREHOUSE = cortex_search_tutorial_wh
    TARGET_LAG = '1 hour'
    AS (
    SELECT
        chunk,
        relative_path,
        file_url,
        language
    FROM cortex_search_tutorial_db.public.doc_chunks
    );

/*
CHECKPOINT - We have a search service,.. Let's put a streamlit app on top of it!
Navigate to streamlit in the left nav pane
*/

--notice... the search service didnt require us to make / store vectors? 
--Let's say though, you didnt want to use the search service, and wanted to embed text as a column as well

create or replace table doc_chunks_vectors clone doc_chunks;
alter table doc_chunks_vectors add column 
    embeddings vector(float,768);

update doc_chunks_vectors set
embeddings = SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m-v1.5', chunk);

--validate
select * from doc_chunks_vectors;


--lets search on it.

-- Embed incoming prompt
SET prompt = 'what are the pension consideration for DCG participation';
CREATE OR REPLACE TABLE prompt_table (prompt_vec VECTOR(FLOAT, 768));
INSERT INTO prompt_table SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_768('snowflake-arctic-embed-m', $prompt);

-- Do a semantic search to find the relevant wiki for the query
WITH result AS (
    SELECT
        w.chunk,
        $prompt AS prompt_text,
        VECTOR_COSINE_SIMILARITY(w.embeddings, q.prompt_vec) AS similarity
    FROM doc_chunks_vectors w, prompt_table q
    ORDER BY similarity DESC
    LIMIT 1
)

-- Pass to large language model as context
SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-7b',
    CONCAT('Answer this question: ', prompt_text, ' using this text: ', chunk)) FROM result;

