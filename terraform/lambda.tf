resource "aws_s3_bucket" "lambda_storage" {
  bucket        = "barcode-lambda-bucket"
  acl           = "private"
  force_destroy = true
}

data "archive_file" "lambda_crafting" {
  type = "zip"

  source_dir  = "./lambda/crafting"
  output_path = "./lambda/crafting.zip"
}

resource "aws_s3_bucket_object" "lambda_hello_world" {
  bucket = aws_s3_bucket.lambda_bucket.id

  key    = "crafting.zip"
  source = data.archive_file.lambda_crafting.output_path

  etag = filemd5(data.archive_file.lambda_crafting.output_path)
}

resource "aws_lambda_function" "crafting" {
  function_name = "HelloWorld"

  s3_bucket        = aws_s3_bucket.lambda_bucket.id
  s3_key           = aws_s3_bucket_object.lambda_hello_world.key
  runtime          = "python3.7"
  handler          = "hello.handler"
  source_code_hash = data.archive_file.lambda_hello_world.output_base64sha256
  role             = aws_iam_role.lambda_exec.arn
}



resource "aws_cloudwatch_log_group" "crafting" {
  name              = "/aws/lambda/${aws_lambda_function.crafting.function_name}"
  retention_in_days = 30
}

resource "aws_iam_role" "lambda_exec" {
  name = "serverless_lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Sid    = ""
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}