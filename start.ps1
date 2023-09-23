# Usage: .\start.ps1
# Requires : opentofu (go), python3
# Execute SetRemoteSignedPolicy the first time to grant execution policy to this script
param(
  [String] $Command
)

function HelpMessage() {
    echo "Usage : ./start.ps1 <command>"
    echo " infraInit        Init infra from scratch"
    echo " infraDestroy     Destroy infra"
    echo " build            Build static pages in public with Python"
}

function InfraInit {
    echo "Building infra ..."
    cd infra
    echo "$env:TF_VAR_AWS_REGION"
    opentofu init
    opentofu plan
    opentofu apply -auto-approve
}

function InfraDestroy {
    echo "Destroying infra ..."
    cd infra
    opentofu version
    opentofu destroy -auto-approve
}

function Build {
    echo "Building static pages ..."
    python src/wavenDbTop.py
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
        } else {
            Set-PSDebug -Trace 0
            echo "Command '$Command' not found."
            HelpMessage
        }
    }
    catch {
        Write-Warning "An error occurred"
    }
    finally {
        CdCurrentDirectory # Back to current directory
        Set-PSDebug -Trace 0
    }
}

Set-PSDebug -Trace 0
$CurrentDir=$PSScriptRoot # Get current directory
Main
