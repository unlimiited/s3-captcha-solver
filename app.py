from flask import Flask, render_template, request, redirect
import boto3
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

S3_BUCKET = os.environ.get('BUCKET_NAME')
UNSOLVED_PREFIX = os.environ.get('UNSOLVED_PREFIX')
SOLVED_PREFIX = os.environ.get('SOLVED_PREFIX')

s3_client = boto3.client(
    service_name ="s3",
    endpoint_url = os.environ.get('ENDPOINT_URL'),
    aws_access_key_id = os.environ.get('ACCESS_KEY_ID'),
    aws_secret_access_key = os.environ.get('SECRET_ACCESS_KEY'),
    region_name="auto",
)

@app.route('/')
def index():
    response = s3_client.list_objects_v2(Bucket=S3_BUCKET, Prefix=UNSOLVED_PREFIX)
    images = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'] != UNSOLVED_PREFIX]
    
    if images:
        image_key = images[0]
        image_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': S3_BUCKET, 'Key': image_key}, ExpiresIn=3600)
    else:
        image_key = None
        image_url = None

    return render_template('index.html', image_url=image_url, image_key=image_key)

@app.route('/process', methods=['POST'])
def process():
    digit_code = request.form['digit_code']
    image_key = request.form['image_key']
    
    new_key = SOLVED_PREFIX + f"{digit_code}.jpg"
    
    s3_client.copy_object(Bucket=S3_BUCKET, CopySource={'Bucket': S3_BUCKET, 'Key': image_key}, Key=new_key)
    
    s3_client.delete_object(Bucket=S3_BUCKET, Key=image_key)
    
    return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
