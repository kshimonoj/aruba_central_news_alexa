# aruba_central_news_alexa
Read Aruba Central News by Alexa

Run this script on AWS Lambda.
It collect network information from Aruba Central and update them to json file on AWS S3 as "central_message.json". 
This json can be feed for Amazon Alexa Flash Briefing.

# What you need to do
1. Create AWS Lambda function by using "Archive.zip". Use template "lambda-canary-python3"
2. Create S3 bucket. 
3. Use Template "lambda-canary-python3"
4. Change IAM policy
5. Change S3 bucket policy
6. Upload central_token.json on the same S3 bucket with your credential.
7. Create Alexa Skill. Use Flash Briefig and choose json URL as URL feed on S3 which created by Lambda function.

# AWS Labmda Environment variables
bucket_name : <your bucket name>
group : <your central group name>
base_url : <your central API url (eg. https://app1-apigw.central.arubanetworks.com) >

# Lambda function
There are both English and Japanese script. Only text messages are different.
Both should be work but never tested in English.
