from __future__ import print_function

import urllib
import psycopg2
import boto3

s3 = boto3.client('s3')
iam_role = "IAM ROLE ARN that Redshift has assigned"
db_database = "Redshift DB Name"
db_user = "Redshift User"
db_password = "Redshift Password"
db_port = "5439"
db_host = "Redshift Host"
query_bucket = "YOUR BUCKET NAME"
query_prefix = "ANY PREFIX FOR FILES IN BUCKET"


def handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))

    try:
        conn = psycopg2.connect("dbname=" + db_database
                                + " user=" + db_user
                                + " password=" + db_password
                                + " port=" + db_port
                                + " host=" + db_host)
		conn.autocommit = True

        query_type = query_prefix + key.split('/')[0] + '.sql'

        cur = conn.cursor()

        if is_file_already_copied(bucket, cur, key):
            result = 'Already uploaded {}/{}, skipped.'.format(bucket, key)
        else:
            copy_to_redshift(bucket, conn, cur, key, query_type)
            result = 'Successfully uploaded {}/{}'.format(bucket, key)

        cur.close()
        conn.close()

        print(result)
        return result
    except Exception as e:
        print(e)
        print('Error saving {}/{}'.format(bucket, key))
        raise e


def copy_to_redshift(bucket, conn, cur, key, query_type):
    query = get_copy_query(bucket, key, query_type, query_bucket)
    cur.execute(query)


def is_file_already_copied(bucket, cur, key):
    uploaded = already_uploaded_query(bucket, key)
    cur.execute(uploaded)
    count = cur.fetchone()
    return count[0] > 0


def get_copy_query(bucket, key, type, query_bucket):
    query = s3.get_object(Bucket=query_bucket, Key=type)

    sql = query['Body'].read() \
        .replace("{{bucket}}", bucket) \
        .replace("{{key}}", key) \
        .replace("{{iam_role}}", iam_role)

    return sql


def already_uploaded_query(bucket, key):
    sql = "select count(1) as total from stl_load_commits where filename = 's3://{}/{}';".format(bucket, key)
    return sql
