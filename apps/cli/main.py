import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional
import requests
from pathlib import Path

from .config import settings


app = typer.Typer(
    name="secondbrain",
    help="SecondBrain CLI - AI-powered knowledge management system",
    no_args_is_help=True,
)

console = Console()


@app.command()
def status():
    """Check API status and health."""
    console.print("🔍 Checking SecondBrain API status...", style="bold blue")

    try:
        response = requests.get(f"{settings.API_BASE_URL}/health/detailed")
        response.raise_for_status()

        health_data = response.json()

        # Create status table
        table = Table(title="SecondBrain Health Status")
        table.add_column("Service", style="cyan")
        table.add_column("Status", justify="center")

        for service, status in health_data.get("checks", {}).items():
            color = "green" if status == "healthy" else "red"
            table.add_row(service.title(), f"[{color}]{status}[/{color}]")

        console.print(table)

        overall_status = health_data.get("status", "unknown")
        if overall_status == "healthy":
            console.print("✅ All services are healthy!", style="bold green")
        else:
            console.print("❌ Some services are unhealthy!", style="bold red")

    except Exception as e:
        console.print(f"❌ Failed to check status: {str(e)}", style="bold red")


@app.command()
def upload(
    vault_path: Path = typer.Argument(..., help="Path to the vault ZIP file"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Vault name"),
):
    """Upload a vault ZIP file."""

    if not vault_path.exists():
        console.print(f"❌ File not found: {vault_path}", style="bold red")
        raise typer.Exit(1)

    if not vault_path.suffix.lower() == ".zip":
        console.print("❌ Only ZIP files are supported", style="bold red")
        raise typer.Exit(1)

    vault_name = name or vault_path.stem

    console.print(f"📤 Uploading vault: {vault_name}", style="bold blue")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Uploading...", total=None)

            with open(vault_path, "rb") as f:
                files = {"file": (vault_path.name, f, "application/zip")}
                data = {"name": vault_name}

                response = requests.post(
                    f"{settings.API_BASE_URL}/api/v1/vaults/upload",
                    files=files,
                    data=data,
                )

                progress.update(task, description="Processing response...")

                if response.status_code == 200:
                    result = response.json()
                    console.print("✅ Vault uploaded successfully!", style="bold green")
                    console.print(f"   ID: {result['id']}")
                    console.print(f"   Name: {result['name']}")
                    console.print(f"   Status: {result['status']}")
                else:
                    console.print(
                        f"❌ Upload failed: HTTP {response.status_code}",
                        style="bold red",
                    )
                    console.print(f"   {response.text}")

    except Exception as e:
        console.print(f"❌ Upload failed: {str(e)}", style="bold red")
        raise typer.Exit(1)


@app.command()
def list():
    """List all vaults."""
    console.print("📚 Listing vaults...", style="bold blue")

    try:
        response = requests.get(f"{settings.API_BASE_URL}/api/v1/vaults/")
        response.raise_for_status()

        vaults = response.json()

        if not vaults:
            console.print("No vaults found.", style="yellow")
            return

        # Create vaults table
        table = Table(title="SecondBrain Vaults")
        table.add_column("Name", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Files", justify="right")
        table.add_column("Size", justify="right")
        table.add_column("Created", justify="center")

        for vault in vaults:
            status_color = {
                "uploaded": "yellow",
                "processing": "blue",
                "completed": "green",
                "failed": "red",
            }.get(vault["status"], "white")

            table.add_row(
                vault["name"],
                f"[{status_color}]{vault['status']}[/{status_color}]",
                str(vault.get("file_count", 0)),
                f"{vault['file_size'] / 1024 / 1024:.1f} MB",
                vault["created_at"][:10],  # Just the date
            )

        console.print(table)

    except Exception as e:
        console.print(f"❌ Failed to list vaults: {str(e)}", style="bold red")


@app.command()
def info(vault_id: str):
    """Get detailed information about a vault."""
    console.print(f"🔍 Getting vault info: {vault_id}", style="bold blue")

    try:
        response = requests.get(f"{settings.API_BASE_URL}/api/v1/vaults/{vault_id}")
        response.raise_for_status()

        vault = response.json()

        # Display vault information
        console.print(f"\n📁 Vault: {vault['name']}", style="bold cyan")
        console.print(f"   ID: {vault['id']}")
        console.print(f"   Status: {vault['status']}")
        console.print(f"   Original File: {vault['original_filename']}")
        console.print(f"   Size: {vault['file_size'] / 1024 / 1024:.1f} MB")
        console.print(f"   Files: {vault.get('file_count', 0)}")
        console.print(f"   Processed: {vault.get('processed_files', 0)}")
        console.print(f"   Created: {vault['created_at']}")
        console.print(f"   Updated: {vault['updated_at']}")

        if vault.get("error_message"):
            console.print(f"   Error: {vault['error_message']}", style="bold red")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            console.print(f"❌ Vault not found: {vault_id}", style="bold red")
        else:
            console.print(f"❌ Failed to get vault info: {str(e)}", style="bold red")
    except Exception as e:
        console.print(f"❌ Failed to get vault info: {str(e)}", style="bold red")


@app.command()
def delete(vault_id: str):
    """Delete a vault."""
    console.print(f"🗑️  Deleting vault: {vault_id}", style="bold red")

    if not typer.confirm("Are you sure you want to delete this vault?"):
        console.print("Operation cancelled.", style="yellow")
        return

    try:
        response = requests.delete(f"{settings.API_BASE_URL}/api/v1/vaults/{vault_id}")
        response.raise_for_status()

        console.print("✅ Vault deleted successfully!", style="bold green")

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            console.print(f"❌ Vault not found: {vault_id}", style="bold red")
        else:
            console.print(f"❌ Failed to delete vault: {str(e)}", style="bold red")
    except Exception as e:
        console.print(f"❌ Failed to delete vault: {str(e)}", style="bold red")


@app.command()
def config():
    """Show current configuration."""
    console.print("⚙️  SecondBrain Configuration", style="bold blue")

    table = Table(title="Current Settings")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("API Base URL", settings.API_BASE_URL)
    table.add_row("Environment", settings.ENVIRONMENT)

    console.print(table)


def cli():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    cli()
