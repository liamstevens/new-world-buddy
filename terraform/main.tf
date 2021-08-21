terraform {
  backend "remote" {
    hostname = "app.terraform.io"
    organization = "feedback-engineering"

    workspaces {
      name = "new-world-buddy"
    }
  }
}

provider "aws" {
  region = "ap-southeast-2"
}