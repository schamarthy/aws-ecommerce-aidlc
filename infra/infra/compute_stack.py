import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3 as s3,
)
from constructs import Construct


class ComputeStack(cdk.Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        vpc: ec2.Vpc,
        sg: ec2.SecurityGroup,
        key_pair: ec2.KeyPair,
        uploads_bucket: s3.Bucket,
        uploads_cf_url: str,
        **kwargs,
    ):
        super().__init__(scope, construct_id, **kwargs)

        # IAM role for EC2 — S3 access to uploads bucket only
        role = iam.Role(
            self, "Ec2Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        )
        uploads_bucket.grant_read_write(role)

        # Amazon Linux 2023 AMI
        ami = ec2.MachineImage.latest_amazon_linux2023()

        # User-data: install Docker, clone repo, run compose
        user_data = ec2.UserData.for_linux()
        user_data.add_commands(
            # System updates + Docker
            "dnf update -y",
            "dnf install -y docker git",
            "systemctl enable docker",
            "systemctl start docker",
            # Docker Compose plugin
            'mkdir -p /usr/local/lib/docker/cli-plugins',
            'curl -SL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/lib/docker/cli-plugins/docker-compose',
            "chmod +x /usr/local/lib/docker/cli-plugins/docker-compose",
            # Add ec2-user to docker group
            "usermod -aG docker ec2-user",
            # Clone repo
            "git clone https://github.com/placeholder/ecommerce.git /app || true",
            "mkdir -p /app",
            # Write .env file (values filled at deploy time via CDK tokens)
            f'echo "S3_BUCKET_NAME={uploads_bucket.bucket_name}" > /app/.env',
            f'echo "S3_IMAGES_CLOUDFRONT_URL={uploads_cf_url}" >> /app/.env',
            'echo "ADMIN_DATABASE_URL=sqlite:////data/admin.db" >> /app/.env',
            'echo "CATALOG_DATABASE_URL=sqlite:////data/admin.db" >> /app/.env',
            'echo "CART_DATABASE_URL=sqlite:////data/cart.db" >> /app/.env',
            'echo "CART_CATALOG_DATABASE_URL=sqlite:////data/admin.db" >> /app/.env',
            'echo "ORDERS_DATABASE_URL=sqlite:////data/orders.db" >> /app/.env',
            'echo "ORDERS_CART_DATABASE_URL=sqlite:////data/cart.db" >> /app/.env',
            'echo "ORDERS_ADMIN_DATABASE_URL=sqlite:////data/admin.db" >> /app/.env',
            'echo "AUTH_DATABASE_URL=sqlite:////data/auth.db" >> /app/.env',
            # JWT secret — generate a random one on first boot
            'echo "AUTH_JWT_SECRET=$(openssl rand -hex 32)" >> /app/.env',
            # Create data volume directory
            "mkdir -p /data",
            # Start services (docker compose build + up)
            "cd /app && docker compose -f docker-compose.prod.yml up --build -d || true",
        )

        # EC2 instance
        self.instance = ec2.Instance(
            self, "EcommerceEc2",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ami,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=sg,
            key_pair=key_pair,
            role=role,
            user_data=user_data,
            block_devices=[
                ec2.BlockDevice(
                    device_name="/dev/xvda",
                    volume=ec2.BlockDeviceVolume.ebs(20),  # 20 GB (within 30 GB free tier)
                )
            ],
        )

        # Elastic IP — stable public IP across stop/start
        eip = ec2.CfnEIP(self, "EcommerceEip")
        ec2.CfnEIPAssociation(
            self, "EipAssociation",
            instance_id=self.instance.instance_id,
            allocation_id=eip.attr_allocation_id,
        )

        # Outputs
        cdk.CfnOutput(self, "Ec2PublicIp", value=eip.ref)
        cdk.CfnOutput(self, "Ec2InstanceId", value=self.instance.instance_id)
        cdk.CfnOutput(
            self, "SshCommand",
            value=f"ssh -i ~/.ssh/ecommerce-key.pem ec2-user@{eip.ref}",
        )
