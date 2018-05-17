#!/bin/bash

curl -XPOST 'localhost:9200/agile_data_science/_search?pretty' -d '
{
    "query": { "match_all": {} }
}
'
