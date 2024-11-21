import os
import boto3
import subprocess
from io import BytesIO

libre_office_install_dir = '/tmp/instdir'

def load_libre_office():
    pass

def download_from_s3(bucket, key, download_path):
    s3 = boto3.client("s3")
    s3.download_file(bucket, key, download_path)

def upload_to_s3(file_path, bucket, key):
    s3 = boto3.client("s3")
    s3.upload_file(file_path, bucket, key)

def convert_word_to_pdf(soffice_path, word_file_path, output_dir):
    conv_cmd = f"{soffice_path} --headless --norestore --invisible --nodefault --nofirststartwizard --nolockcheck --nologo --convert-to pdf:writer_pdf_Export --outdir {output_dir} {word_file_path}"
    response = subprocess.run(conv_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if response.returncode != 0:
        return False
    return True

def lambda_handler(event, context):
    s3_uri = event['s3Uri']
    bucket, key = s3_uri.replace("s3://", "").split("/", 1)
    
    key_prefix, base_name = os.path.split(key)
    download_path = f"/tmp/{base_name}"
    output_dir = "/tmp"
    
    download_from_s3(bucket, key, download_path)
    soffice_path = load_libre_office()

    is_converted = convert_word_to_pdf(soffice_path, download_path, output_dir)
    
    if is_converted:
        file_name, _ = os.path.splitext(base_name)
        upload_to_s3(f"{output_dir}/{file_name}.pdf", bucket, f"{key_prefix}/{file_name}.pdf")
        return {"response": f"File converted to PDF and available at s3://{bucket}/{key_prefix}/{file_name}.pdf"}
    else:
        return {"response": "Cannot convert this document to PDF"}
def lambda_handler(event, context):
    try:
        apiPath = event.get('apiPath', None)  
        if not apiPath:
            raise ValueError("Missing 'apiPath' in the event")

        
        return {"response": "API path is successfully retrieved"}

    except ValueError as e:
        return {"error": str(e)}

    except KeyError as e:
        return {"error": f"Missing key in event: {str(e)}"}

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
