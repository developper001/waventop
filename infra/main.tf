locals {
  dot_env_file_path = "../.env"
  dot_env_regex = "(?m:^\\s*([^#\\s]\\S*)\\s*=\\s*[\"']?(.*[^\"'\\s])[\"']?\\s*$)"
  dot_env = { for tuple in regexall(local.dot_env_regex, file(local.dot_env_file_path)) : tuple[0] => sensitive(tuple[1]) }
  AWS_ACCESS_KEY = local.dot_env["AWS_ACCESS_KEY"]
  AWS_SECRET_KEY = local.dot_env["AWS_SECRET_KEY"]
  AWS_REGION = local.dot_env["AWS_REGION"]
}

provider "aws" {
  access_key = local.AWS_ACCESS_KEY
  secret_key = local.AWS_SECRET_KEY
  region = local.AWS_REGION
}

resource "aws_s3_bucket" "waventop-bucket" {
  bucket = "waventop-bucket"
  force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "waventop-bucket" {
  bucket = aws_s3_bucket.waventop-bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Directory ./public/ is uploaded to s3
resource "aws_s3_object" "provision_source_files" {
  bucket = aws_s3_bucket.waventop-bucket.id
  for_each = fileset("../public/", "**/*.*")
  key = each.value
  source = "../public/${each.value}"
  content_type = each.value
}

# resource "aws_s3_bucket_policy" "bucket_policy" {
#   bucket = aws_s3_bucket.waventop.id

#   policy = <<POLICY
# {
#   "Version":"2012-10-17",
#   "Statement":[
#     {
#       "Sid":"PublicReadGetObject",
#       "Effect":"Allow",
#       "Principal": "*",
#       "Action":["s3:GetObject"],
#       "Resource":["arn:aws:s3:::${aws_s3_bucket.waventop.id}/*"]
#     }
#   ]
# }
# POLICY
# }
