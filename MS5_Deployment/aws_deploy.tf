provider "aws" { region = "eu-central-1" }

# ECR Repos
resource "aws_ecr_repository" "cloud_a" { name = "soil-cloud-a" }
resource "aws_ecr_repository" "cloud_b" { name = "soil-cloud-b" }

# ECS Cluster (Fargate)
resource "aws_ecs_cluster" "soil" {
  name = "soil-analyzer-cluster"
  capacity_providers = ["FARGATE"]
}

# Task Definition Cloud A
resource "aws_ecs_task_definition" "cloud_a" {
  family = "soil-cloud-a"
  network_mode = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu = 256
  memory = 512
  execution_role_arn = aws_iam_role.ecs_task.arn
  
  container_definitions = jsonencode([{
    name  = "cloud-a"
    image = "${aws_ecr_repository.cloud_a.repository_url}:latest"
    portMappings = [{ containerPort = 8080 }]
  }])
}

# Service
resource "aws_ecs_service" "cloud_a" {
  name            = "soil-cloud-a-service"
  cluster         = aws_ecs_cluster.soil.id
  task_definition = aws_ecs_task_definition.cloud_a.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets         = ["subnet-xxxx"]  # Deine VPC Subnets
    security_groups = [aws_security_group.ecs.id]
    assign_public_ip = true
  }
}

# Security Group
resource "aws_security_group" "ecs" {
  ingress { from_port = 8080; to_port = 8080; protocol = "tcp"; cidr_blocks = ["0.0.0.0/0"] }
  egress { from_port = 0; to_port = 0; protocol = "-1"; cidr_blocks = ["0.0.0.0/0"] }
}

# IAM Role (vereinfacht)
resource "aws_iam_role" "ecs_task" {
  name = "ecsTaskExecutionRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}
resource "aws_iam_role_policy_attachment" "ecs_task" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
