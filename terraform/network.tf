resource "aws_vpc" "main" {
    cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "main_ap" {
  vpc_id = aws_vpc.main.id
  cidr_block = "10.0.0.1/24"
  tags {
      Name = "new-world-buddy"
  }
}

resource "aws_security_group" "ssh_access" {
  name        = "allow_ssh"
  description = "Allow SSH inbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress = [
    {
      description      = "SSH from VPC"
      from_port        = 22
      to_port          = 22
      protocol         = "tcp"
      cidr_blocks      = [aws_vpc.main.cidr_block, "180.150.37.87/32"]
      ipv6_cidr_blocks = [aws_vpc.main.ipv6_cidr_block]
    }
  ]
}