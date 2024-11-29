resource "aws_s3_bucket" "example" {
  bucket = "seneator"

  tags = {
    Name        = "My bucket"
    Environment = "Dev"
  }
  
}