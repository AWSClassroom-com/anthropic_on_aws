"""
Lab 1 Setup Verification Script
Anthropic Models on AWS Bedrock
 
Checks that all prerequisites are in place before starting Lab 1.
Run this script after completing Part 1 setup steps.
"""
 
import sys
import importlib.util
 
DOCUMENT_PREFIX = "lab1-documents/"
REQUIRED_PYTHON = (3, 11)
REQUIRED_DOCUMENTS = 5
REGION = "us-east-1"
 
PASS = "\033[92mOK\033[0m"
FAIL = "\033[91mFAIL\033[0m"
WIDTH = 40
 
 
def check(label, status, detail=""):
    result = PASS if status else FAIL
    print(f"  {label:<{WIDTH}} {result}{'  ' + detail if detail else ''}")
    return status
 
 
def check_python():
    version = sys.version_info
    ok = (version.major, version.minor) >= REQUIRED_PYTHON
    detail = f"({version.major}.{version.minor}.{version.micro})"
    return check("Python version...", ok, detail)
 
 
def check_boto3():
    spec = importlib.util.find_spec("boto3")
    if spec is None:
        check("boto3 installed...", False, "(run: pip install boto3)")
        return False
    import boto3
    return check("boto3 installed...", True, f"({boto3.__version__})")
 
 
def check_dotenv():
    spec = importlib.util.find_spec("dotenv")
    if spec is None:
        check("python-dotenv installed...", False, "(run: pip install python-dotenv)")
        return False
    return check("python-dotenv installed...", True)
 
 
def boto3_available():
    return importlib.util.find_spec("boto3") is not None
 
 
def get_account_id():
    """Return the AWS account ID from STS, or None on failure."""
    try:
        import boto3
        sts = boto3.client("sts", region_name=REGION)
        return sts.get_caller_identity().get("Account")
    except Exception:
        return None
 
 
def build_bucket_name(account_id):
    return f"bedrock-training-{account_id}"
 
 
def check_credentials():
    if not boto3_available():
        return check("AWS credentials...", False, "(boto3 not installed -- install it first)"), None
 
    try:
        import boto3
        from botocore.exceptions import NoCredentialsError, ClientError
        sts = boto3.client("sts", region_name=REGION)
        identity = sts.get_caller_identity()
        arn = identity.get("Arn", "")
        account_id = identity.get("Account", "")
        username = arn.split("/")[-1] if "/" in arn else arn
        return check("AWS credentials...", True, f"({username})"), account_id
    except NoCredentialsError:
        check("AWS credentials...", False, "(no credentials found)")
        print(f"\n  Run 'aws login' and complete the browser prompt, then retry.\n")
        return False, None
    except ClientError as e:
        code = e.response["Error"]["Code"]
        check("AWS credentials...", False, f"({code})")
        print(f"\n  AWS returned an error: {code}")
        print(f"  Run 'aws sts get-caller-identity' to diagnose.\n")
        return False, None
    except Exception as e:
        msg = str(e)
        if "MissingDependency" in msg or "botocore[crt]" in msg:
            check("AWS credentials...", False, "(missing botocore[crt])")
            print(f"\n  Run: pip install 'botocore[crt]'")
            print(f"  Then retry this script.\n")
        else:
            check("AWS credentials...", False, f"({type(e).__name__}: {e})")
        return False, None
 
 
def check_s3_access(bucket_name):
    if not boto3_available():
        return check("S3 bucket access...", False, "(boto3 not installed -- install it first)")
 
    try:
        import boto3
        from botocore.exceptions import ClientError
        s3 = boto3.client("s3", region_name=REGION)
        s3.head_bucket(Bucket=bucket_name)
        return check("S3 bucket access...", True, f"(s3://{bucket_name})")
    except ClientError as e:
        code = e.response["Error"]["Code"]
        check("S3 bucket access...", False, f"({code})")
        print(f"\n  Could not access s3://{bucket_name}")
        print(f"  Ask your instructor to confirm your IAM permissions.\n")
        return False
    except Exception as e:
        check("S3 bucket access...", False, f"({type(e).__name__}: {e})")
        return False
 
 
def check_documents(bucket_name):
    if not boto3_available():
        return check("Sample documents...", False, "(boto3 not installed -- install it first)")
 
    try:
        import boto3
        from botocore.exceptions import ClientError
        s3 = boto3.client("s3", region_name=REGION)
        response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix=DOCUMENT_PREFIX
        )
        objects = [
            o for o in response.get("Contents", [])
            if not o["Key"].endswith("/")
        ]
        count = len(objects)
        ok = count >= REQUIRED_DOCUMENTS
        detail = f"({count} document{'s' if count != 1 else ''} found)"
        if not ok:
            check("Sample documents...", False, detail)
            print(f"\n  Expected at least {REQUIRED_DOCUMENTS} documents at")
            print(f"  s3://{bucket_name}/{DOCUMENT_PREFIX}")
            print(f"  Ask your instructor to confirm the bucket contents.\n")
            return False
        return check("Sample documents...", True, detail)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        check("Sample documents...", False, f"({code})")
        return False
    except Exception as e:
        check("Sample documents...", False, f"({type(e).__name__}: {e})")
        return False
 
 
def main():
    print()
    print("=" * 55)
    print("  Lab 1 Setup Verification")
    print("  Anthropic Models on AWS Bedrock")
    print("=" * 55)
    print()
 
    python_ok = check_python()
    boto3_ok = check_boto3()
    dotenv_ok = check_dotenv()
    creds_ok, account_id = check_credentials()
    bucket_name = build_bucket_name(account_id) if account_id else "bedrock-training-unknown"
 
    results = [
        python_ok,
        boto3_ok,
        dotenv_ok,
        creds_ok,
        check_s3_access(bucket_name),
        check_documents(bucket_name),
    ]
 
    print()
 
    if all(results):
        print("=" * 55)
        print("  Setup complete. Ready to start Lab 1.")
        print("=" * 55)
        print()
        sys.exit(0)
    else:
        failed = results.count(False)
        print("=" * 55)
        print(f"  {failed} check{'s' if failed != 1 else ''} failed.")
        print("  Resolve the issues above before continuing.")
        print("=" * 55)
        print()
        sys.exit(1)
 
 
if __name__ == "__main__":
    main()