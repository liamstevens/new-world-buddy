data "archive_file" "bot" {
  type        = "zip"
  source_dir  = "../bot"
  output_path = "../bot/bot.zip"
}

resource "aws_s3_bucket" "bootstrap" {
  bucket        = "new-world-buddy-bootstrap"
  acl           = "private"
  force_destroy = true
}

resource "aws_s3_bucket_object" "bot_bootstrap" {
  bucket = aws_s3_bucket.bootstrap.id

  key    = "bot.zip"
  source = data.archive_file.bot.output_path

  etag = filemd5(data.archive_file.bot.output_path)
}

resource "aws_iam_role" "new_world_buddy_role" {
  name = "new-world-buddy"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Sid    = ""
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "new_world_buddy_policy" {
  name = "nwb-s3-access-policy"
  role = aws_iam_role.new_world_buddy_role.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:Get*",
          "s3:List*"
        ]
        Effect   = "Allow"
        Resource = "${aws_s3_bucket.bootstrap.arn}"
      },
    ]
  })
}

resource "aws_iam_instance_profile" "bot_instance_profile" {
  name = "bot_profile"
  role = aws_iam_role.new_world_buddy_role.name
}

resource "aws_instance" "bot_instance" {
  ami           = "ami-0210560cedcb09f07"
  instance_type = "t2.micro"

  subnet_id            = aws_subnet.main_ap.id
  security_groups      = [aws_security_group.ssh_access.id]
  user_data            = <<EOF
    aws s3 cp s3://new-world-buddy-bootstrap/bot.zip ./bot.zip
    unzip bot.zip
    yum install python3
    pip3 install ./bot/requirements.txt
    python3 ./bot/buddy-bot.py
    EOF
  iam_instance_profile = aws_iam_instance_profile.bot_instance_profile.id
}