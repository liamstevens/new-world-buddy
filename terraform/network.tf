resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "main_ap" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"

  tags = {
    Name = "new-world-buddy"
  }
}

resource "aws_security_group" "ssh_access" {
  name        = "allow_ssh"
  description = "Allow SSH inbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress = [
    {
      self             = null
      prefix_list_ids  = null
      security_groups  = null
      description      = "SSH from VPC"
      from_port        = 22
      to_port          = 22
      protocol         = "tcp"
      cidr_blocks      = [aws_vpc.main.cidr_block, "180.150.37.87/32"]
      ipv6_cidr_blocks = [aws_vpc.main.ipv6_cidr_block]
    }
  ]
  egress = [
    {
      description      = "Egress out to world"
      self             = null
      prefix_list_ids  = null
      security_groups  = null
      from_port        = 0
      to_port          = 0
      protocol         = "-1"
      cidr_blocks      = ["0.0.0.0/0"]
      ipv6_cidr_blocks = ["::/0"]
    }
  ]
}