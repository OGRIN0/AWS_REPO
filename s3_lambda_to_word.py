import os
import boto3
import subprocess

libre_office_install_dir = '/tmp/instdir'

def load_libre_office():
  
    soffice_path = f"{libre_office_install_dir}/program/soffice"
    if not os.path.exists(soffice_path):
        raise FileNotFoundError("LibreOffice binary not found. Ensure it is installed in the specified directory.")
    return soffice_path

def download_from_s3(bucket, key, download_path):
  
    s3 = boto3.client("s3")
    s3.download_file(bucket, key, download_path)

def upload_to_s3(file_path, bucket, key):
    
    s3 = boto3.client("s3")
    s3.upload_file(file_path, bucket, key)

def convert_word_to_pdf(soffice_path, word_file_path, output_dir):
    
    conv_cmd = f"{soffice_path} --headless --convert-to pdf:writer_pdf_Export --outdir {output_dir} {word_file_path}"
    response = subprocess.run(conv_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if response.returncode != 0:
        print("LibreOffice Error:", response.stderr.decode("utf-8"))
        return False
    return True

def lambda_handler(event, context):
   
    try:
        s3_uri = event.get('s3Uri')
        if not s3_uri:
            raise ValueError("Missing 's3Uri' in the event")
        
        bucket, key = s3_uri.replace("s3://", "").split("/", 1)
        key_prefix, base_name = os.path.split(key)
        
        download_path = f"/tmp/{base_name}"
        output_dir = "/tmp"
        
        download_from_s3(bucket, key, download_path)
        
        soffice_path = load_libre_office()
        
        is_converted = convert_word_to_pdf(soffice_path, download_path, output_dir)
        if not is_converted:
            raise Exception("Conversion to PDF failed.")
        
        file_name, _ = os.path.splitext(base_name)
        pdf_path = f"{output_dir}/{file_name}.pdf"
        upload_to_s3(pdf_path, bucket, f"{key_prefix}/{file_name}.pdf")
        
        return {"response": f"File converted to PDF and available at s3://{bucket}/{key_prefix}/{file_name}.pdf"}
    
    except ValueError as ve:
        return {"error": str(ve)}
    except FileNotFoundError as fe:
        return {"error": str(fe)}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
