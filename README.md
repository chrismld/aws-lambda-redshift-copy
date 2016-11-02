# AWS Lambda - Redshift Copy
I had the need of automate the copy command to Redshift but couldn't find much information about how to do it, so this is why I decided to share this piece of simple code.

# How it works and how can I configure it?
The script is coded in a way that you can easily set the desired configurations, the initial section has a list of global variables where I have put a description of what you should put there but I think it worths explaining how it works:

First, this lambda receives a notification from S3, then it gets the bucket and the key, based on the prefix of the file it gets the copy query from another bucket and then do some replacements to finally build the copy query that will run in the destination. Before executing the copy, it checks if the file has not been copied yet, this is to make the lambda function idempotent.

# What will I need to make it work?
1. S3 Bucket where you will store your copy queries (it can be one)
1.1 (Optional) A prefix where you will store your copy queries, i.e. queries/
2. IAM Role ARN that the destination Redshift has assigned
3. Host, user, (port?) and password of the destination Redshift 

# How to upload this to AWS Lambda?
You just need to follow this simple steps:
1. Zip all the content of the src folder (including the psycopg2 folder)
2. Upload the zip file to AWS Lambda (you will be able to see the code there but not the psycopg2 library)

# Why do we need to have psycopg2 included?
AWS Lambda doesn't have native support (at least yet) to execute queries into Redshift and when a library is not included in the stack, you need to include all libraries needed in the package (zip) that you upload to lambda.

# How is this useful?
Well, I've used this to replicate in real time the data from one Redshift to another Redshift cluster. For example, imagine that you need to store data from Firehose, you configure your stream in a way that it will convert the data in files and it will store the files in S3, so that it can be executed the copy query that will upload the data to Redshift, but what happens if you would like to upload this data to another cluster (maybe for development purposes). Easy, you just need to configure an event trigger in the S3 bucket, and done! How? this is how: http://docs.aws.amazon.com/lambda/latest/dg/with-s3.html

# Questions or suggestions?
Easy, just send me an email or open an issue :)
