import aws_cdk as cdk
from aws_cdk import (
    aws_s3 as s3,
    aws_cloudfront as cf,
    aws_cloudfront_origins as origins,
)
from constructs import Construct


class StorageStack(cdk.Stack):
    def __init__(self, scope: Construct, construct_id: str, ec2_ip: str = "", **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        account = self.account

        # --- S3 Buckets ---

        # Product image uploads (private, served via CloudFront)
        self.uploads_bucket = s3.Bucket(
            self, "UploadsBucket",
            bucket_name=f"ecommerce-uploads-{account}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.RETAIN,
        )

        # catalog-ui static frontend
        self.catalog_ui_bucket = s3.Bucket(
            self, "CatalogUiBucket",
            bucket_name=f"ecommerce-catalog-ui-{account}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # admin-ui static frontend
        self.admin_ui_bucket = s3.Bucket(
            self, "AdminUiBucket",
            bucket_name=f"ecommerce-admin-ui-{account}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        # --- CloudFront Distributions ---

        # Uploads distribution (serves product images)
        uploads_oac = cf.S3OriginAccessControl(self, "UploadsOac")
        uploads_dist = cf.Distribution(
            self, "UploadsDist",
            default_behavior=cf.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(
                    self.uploads_bucket,
                    origin_access_control=uploads_oac,
                ),
                viewer_protocol_policy=cf.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cf.CachePolicy.CACHING_OPTIMIZED,
            ),
        )
        self.uploads_cf_url = f"https://{uploads_dist.distribution_domain_name}"

        # EC2 API origin (for /api/* behaviors) — only added when ec2_ip is provided
        ec2_origin = origins.HttpOrigin(ec2_ip, protocol_policy=cf.OriginProtocolPolicy.HTTP_ONLY) if ec2_ip else None
        api_behavior = cf.BehaviorOptions(
            origin=ec2_origin,
            viewer_protocol_policy=cf.ViewerProtocolPolicy.ALLOW_ALL,
            cache_policy=cf.CachePolicy.CACHING_DISABLED,
            allowed_methods=cf.AllowedMethods.ALLOW_ALL,
            origin_request_policy=cf.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
        ) if ec2_origin else None

        # catalog-ui distribution
        catalog_oac = cf.S3OriginAccessControl(self, "CatalogUiOac")
        catalog_dist = cf.Distribution(
            self, "CatalogUiDist",
            default_behavior=cf.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(
                    self.catalog_ui_bucket,
                    origin_access_control=catalog_oac,
                ),
                viewer_protocol_policy=cf.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cf.CachePolicy.CACHING_OPTIMIZED,
            ),
            additional_behaviors={"/api/*": api_behavior} if api_behavior else {},
            default_root_object="index.html",
            error_responses=[
                cf.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
                cf.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
            ],
        )

        # admin-ui distribution
        admin_oac = cf.S3OriginAccessControl(self, "AdminUiOac")
        admin_dist = cf.Distribution(
            self, "AdminUiDist",
            default_behavior=cf.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(
                    self.admin_ui_bucket,
                    origin_access_control=admin_oac,
                ),
                viewer_protocol_policy=cf.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cf.CachePolicy.CACHING_OPTIMIZED,
            ),
            additional_behaviors={"/api/*": api_behavior} if api_behavior else {},
            default_root_object="index.html",
            error_responses=[
                cf.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
                cf.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                ),
            ],
        )

        # --- Outputs ---
        cdk.CfnOutput(self, "UploadsBucketName", value=self.uploads_bucket.bucket_name)
        cdk.CfnOutput(self, "UploadsCloudfrontUrl", value=self.uploads_cf_url)
        cdk.CfnOutput(self, "CatalogUiCloudfrontUrl", value=f"https://{catalog_dist.distribution_domain_name}")
        cdk.CfnOutput(self, "AdminUiCloudfrontUrl", value=f"https://{admin_dist.distribution_domain_name}")
        cdk.CfnOutput(self, "CatalogUiBucketName", value=self.catalog_ui_bucket.bucket_name)
        cdk.CfnOutput(self, "AdminUiBucketName", value=self.admin_ui_bucket.bucket_name)
