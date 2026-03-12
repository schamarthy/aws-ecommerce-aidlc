import aws_cdk as cdk
from aws_cdk import (
    aws_ec2 as ec2,
)
from constructs import Construct


class NetworkStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # VPC with 1 public subnet only — no NAT Gateway (free tier)
        self.vpc = ec2.Vpc(
            self, "EcommerceVpc",
            max_azs=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24,
                )
            ],
            nat_gateways=0,
        )

        # Security group for EC2
        self.ec2_sg = ec2.SecurityGroup(
            self, "Ec2Sg",
            vpc=self.vpc,
            description="Allow HTTP and SSH to EC2",
            allow_all_outbound=True,
        )
        self.ec2_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "HTTP")
        self.ec2_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(22), "SSH")

        # EC2 Key Pair
        self.key_pair = ec2.KeyPair(
            self, "EcommerceKeyPair",
            key_pair_name="ecommerce-key",
        )

        # Outputs
        cdk.CfnOutput(self, "VpcId", value=self.vpc.vpc_id)
        cdk.CfnOutput(self, "KeyPairName", value=self.key_pair.key_pair_name)
