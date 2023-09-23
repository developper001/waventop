# Usage: .\start.ps1
# Requires : python3, opentofu (go), aws cli, jq
# Execute SetRemoteSignedPolicy the first time to grant execution policy to this script
param(
  [String] $Command
)

function HelpMessage() {
    echo "Usage : ./start.ps1 <command>"
    echo " infraInit        Init infra from scratch"
    echo " infraDestroy     Destroy infra"
    echo " build            Build static pages in public with Python"
    echo " sync             Upload local files to the s3 bucket"
    echo " run              Build and sync if infra already exists"
}

function InfraInit {
    echo "Building infra ..."
    cd infra
    echo "$env:TF_VAR_AWS_REGION"
    opentofu init
    opentofu plan
    opentofu apply -auto-approve
    opentofu output -json > ./tf_output.json
}

function InfraDestroy {
    echo "Destroying infra ..."
    cd infra
    opentofu version
    opentofu destroy -auto-approve
}

function Build {
    echo "Building static pages ..."
    python src/wavenTop.py
}

function Sync {
    echo "Sync static pages ..."
    $tfoutput = (Get-Content 'infra\tf_output.json' | Out-String | ConvertFrom-Json)
    $s3_bucket_id = $tfoutput.bucket_id.value
    $s3_uri = $tfoutput.object_s3_uri.value
    aws configure set region "$env:AWS_REGION"
    aws configure set aws_access_key_id "$env:AWS_ACCESS_KEY"
    aws configure set aws_secret_access_key "$env:AWS_SECRET_KEY"
    aws s3 sync --delete "./public" "s3://$s3_bucket_id"
    echo "[Success] WavenTop available at $s3_uri"
}

function Run {
    Build
    Sync
}

function CdCurrentDirectory {
    cd $CurrentDir
}

function Main {
    try {
        Set-PSDebug -Trace 1
        # .env
        if (!(Test-Path "$CurrentDir\.env")) {
            Copy-Item "$CurrentDir\.env.tpl" "$CurrentDir\.env"
        }
        get-content .env | foreach {
            $name, $value = $_.split('=')
            set-content env:\$name $value
        }
        # Command to function
        if ($Command -eq "infraInit") {
            InfraInit
        } elseif ($Command -eq "infraDestroy") {
            InfraDestroy
        } elseif ($Command -eq "build") {
            Build
        } elseif ($Command -eq "sync") {
            Sync
        } elseif ($Command -eq "run") {
            Run
        } else {
            Set-PSDebug -Trace 0
            echo "Command '$Command' not found."
            HelpMessage
        }
    }
    catch {
        Write-Warning "$_"
    }
    finally {
        CdCurrentDirectory # Back to current directory
        Set-PSDebug -Trace 0
    }
}

Set-PSDebug -Trace 0
$CurrentDir=$PSScriptRoot # Get current directory
Main
