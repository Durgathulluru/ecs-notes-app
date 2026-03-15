Project Theme

Cloud-Native Notes Application Demonstrating Stateful vs Stateless Architecture on AWS

This project demonstrates the design, containerization, CI/CD automation, and secure deployment of a cloud-native application while showcasing the architectural differences between stateful and stateless services in distributed environments.

The application is a modern Flask-based Notes App deployed using containers, CI/CD pipelines, AWS infrastructure, and secure identity federation.

The project highlights how sticky sessions, container scaling, and externalized data storage impact application behavior in production environments.

⸻

Project Objectives

The primary goals of this project were to demonstrate:
	1.	Containerized application development
	2.	Modern CI/CD pipelines
	3.	Secure cloud identity integration
	4.	Stateful vs Stateless service behavior
	5.	Infrastructure best practices
	6.	Production-style deployment architecture

⸻

High Level Architecture
Developer
   │
   │ git push
   ▼
GitHub Repository
   │
   ▼
GitHub Actions CI/CD
   │
   │ OIDC authentication
   ▼
AWS IAM Role (No static credentials)
   │
   ▼
Amazon ECR
(Container Registry)
   │
   ▼
Amazon ECS (Fargate)
   │
   ▼
Application Load Balancer
   │
   ▼
Containerized Flask Notes App
   │
   ├── Stateful Version (in-memory)
   └── Stateless Version (DynamoDB)

  Key Components Used

  Application Features

User Interface

A modern web interface allows users to:
	•	write notes
	•	auto-save drafts
	•	save notes manually
	•	view application instance metadata

The UI dynamically displays:
Instance ID
AWS Region
Availability Zone
Two Application Modes

The project demonstrates two different service models.

⸻

Mode 1 — Stateful Architecture

In this mode:
	•	Notes are stored in application memory
	•	Each container maintains its own state
	•	If traffic shifts to another container, notes disappear

Behavior
User → Container A → note saved
User → Container B → note missing

Mode 2 — Stateless Architecture

In the stateless model:
	•	Data is stored in DynamoDB
	•	Containers remain completely stateless
	•	Any container can serve the request

Behavior
User → Container A → save note
User → Container B → note still available

Sticky Session Demonstration

The project also demonstrates Application Load Balancer session affinity.

Two scenarios are tested:

Sticky Sessions Enabled

Requests from the same user always hit the same container.

Result:
User → Container A
User → Container A
User → Container A

Sticky Sessions Disabled

Requests are distributed across containers.

Result:
User → Container A
User → Container B
User → Container C

CI/CD Pipeline Architecture
Developer Push
      │
      ▼
GitHub Actions Pipeline
      │
      ▼
Docker Build
      │
      ▼
Push Image to Amazon ECR
      │
      ▼
Deploy to ECS

The pipeline automatically:
	•	builds the Docker image
	•	tags images with commit SHA
	•	pushes images to ECR
	•	prepares them for deployment

  Secure Identity Integration (OIDC)

Instead of storing AWS credentials in GitHub, the pipeline uses OIDC federation.
GitHub → OIDC Token → AWS IAM Role
Benefits:
	•	No static AWS credentials
	•	Temporary role assumption
	•	Strong security posture

This follows AWS recommended security practices.
Security Architecture

Security was implemented across several layers.

Identity Security

GitHub Actions authenticates to AWS using:
OIDC Identity Federation
This removes the need for:
AWS_ACCESS_KEY
AWS_SECRET_KEY

Least Privilege IAM

The IAM role allows only:
ecr:GetAuthorizationToken
ecr:UploadLayerPart
ecr:PutImage
ecr:BatchCheckLayerAvailability

It cannot:
	•	modify other AWS services
	•	access EC2
	•	access S3
	•	delete repositories

Container Security

The container image uses:
python:3.11-slim
Benefits:
	•	minimal attack surface
	•	reduced vulnerabilities
	•	smaller image size

Network Security

The architecture uses:
VPC
Private Subnets
Security Groups

Access is restricted to:
ALB → ECS Tasks
Direct public container exposure is avoided.

Registry Security
ECR uses:
    image vulnerability scanning
Every pushed image is automatically scanned for:
	•	CVEs
	•	dependency vulnerabilities

  Infrastructure Security

Best practices applied:
	•	IAM role-based access
	•	encrypted image storage
	•	secure token authentication
	•	minimal attack surface containers
Operational Capabilities Demonstrated

The project demonstrates real-world DevOps skills including:
	•	containerized application development
	•	CI/CD pipeline design
	•	cloud identity federation
	•	infrastructure automation
	•	secure container registry usage
	•	distributed application architecture
  Project Accomplishments

Cloud Engineering

Designed and deployed a containerized cloud-native application architecture on AWS using ECS, ECR, and ALB.

⸻

DevOps Automation

Built an automated CI/CD pipeline using GitHub Actions to build Docker images and push them to Amazon ECR.

⸻

Secure Authentication

Implemented GitHub OIDC authentication with AWS IAM roles, eliminating static credentials and improving security posture.

⸻

Distributed Architecture Demonstration

Successfully demonstrated the operational differences between:
  Stateful services
  Stateless services

  Load Balancer Session Management

Demonstrated ALB sticky sessions and how session affinity impacts application behavior.

⸻

Secure Infrastructure Design

Applied least privilege IAM policies and secure container registries to follow cloud security best practices

