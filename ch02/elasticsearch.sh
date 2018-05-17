curl -XPUT 'localhost:9200/customer/external/1?pretty' -d '
{
  "name": "Russell Jurney"
}'

curl -XGET 'localhost:9200/customer/external/1?pretty'
