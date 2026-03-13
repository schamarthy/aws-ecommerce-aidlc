#!/usr/bin/env python3
import aws_cdk as cdk

from infra.network_stack import NetworkStack
from infra.storage_stack import StorageStack
from infra.compute_stack import ComputeStack

env = cdk.Environment(account="074412166767", region="us-west-2")

app = cdk.App()

network = NetworkStack(app, "NetworkStack", env=env)
storage = StorageStack(app, "StorageStack", ec2_ip="ec2-100-22-44-133.us-west-2.compute.amazonaws.com", env=env)
compute = ComputeStack(
    app, "ComputeStack",
    vpc=network.vpc,
    sg=network.ec2_sg,
    key_pair=network.key_pair,
    uploads_bucket=storage.uploads_bucket,
    uploads_cf_url=storage.uploads_cf_url,
    env=env,
)

app.synth()
