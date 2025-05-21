# Terraform Management Makefile

# Variables
TF_DIR := terraform
ENV ?= dev

.PHONY: tf-init tf-plan tf-apply tf-destroy tf-validate tf-format help

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z\-_0-9]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

tf-init: ## Initialize Terraform
	cd $(TF_DIR) && terraform init

tf-plan: ## Generate and show Terraform execution plan (ENV=dev|staging|prod)
	cd $(TF_DIR) && terraform plan -var-file=terraform.tfvars -var="environment=$(ENV)"

tf-apply: ## Build or change infrastructure (ENV=dev|staging|prod)
	cd $(TF_DIR) && terraform apply -var-file=terraform.tfvars -var="environment=$(ENV)"

tf-destroy: ## Destroy Terraform-managed infrastructure (ENV=dev|staging|prod)
	@echo "Are you sure you want to destroy the $(ENV) environment? [y/N]" && read ans && [ $${ans:-N} = y ]
	cd $(TF_DIR) && terraform destroy -var-file=terraform.tfvars -var="environment=$(ENV)"

tf-validate: ## Validate Terraform configuration files
	cd $(TF_DIR) && terraform validate

tf-format: ## Format Terraform configuration files
	cd $(TF_DIR) && terraform fmt -recursive

tf-workspace-new: ## Create a new workspace (ENV=dev|staging|prod)
	cd $(TF_DIR) && terraform workspace new $(ENV)

tf-workspace-select: ## Select a workspace (ENV=dev|staging|prod)
	cd $(TF_DIR) && terraform workspace select $(ENV)

tf-workspace-list: ## List workspaces
	cd $(TF_DIR) && terraform workspace list

tf-output: ## Show output values (ENV=dev|staging|prod)
	cd $(TF_DIR) && terraform output
