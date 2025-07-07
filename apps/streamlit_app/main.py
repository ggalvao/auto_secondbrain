"""Streamlit application for SecondBrain."""

from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import requests
import streamlit as st

from .config import settings

st.set_page_config(
    page_title="SecondBrain",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Run the main Streamlit application."""
    st.title("🧠 SecondBrain")
    st.markdown("AI-powered knowledge management system")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page", ["Upload Vault", "Vault Management", "Analytics", "Settings"]
    )

    if page == "Upload Vault":
        upload_vault_page()
    elif page == "Vault Management":
        vault_management_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Settings":
        settings_page()


def upload_vault_page() -> None:
    """Display the vault upload page."""
    st.header("📁 Upload Obsidian Vault")

    with st.form("vault_upload"):
        st.markdown("Upload your Obsidian vault as a ZIP file for processing.")

        name = st.text_input("Vault Name", placeholder="My Knowledge Base")
        uploaded_file = st.file_uploader(
            "Choose ZIP file",
            type=["zip"],
            help="Upload your Obsidian vault as a ZIP file",
        )

        submit_button = st.form_submit_button("Upload Vault")

        if submit_button:
            if not name.strip():
                st.error("Please enter a vault name")
                return

            if uploaded_file is None:
                st.error("Please select a ZIP file")
                return

            # Upload vault
            with st.spinner("Uploading vault..."):
                try:
                    response = upload_vault(name, uploaded_file)

                    if response.get("status") == "success":
                        st.success("✅ Vault uploaded successfully!")
                        st.info(f"Vault ID: {response.get('vault_id')}")
                        st.info(
                            "Processing has started. Check the Vault "
                            "Management page for status."
                        )
                    else:
                        st.error(
                            f"Upload failed: {response.get('message', 'Unknown error')}"
                        )

                except Exception as e:
                    st.error(f"Upload failed: {str(e)}")


def vault_management_page() -> None:
    """Display the vault management page."""
    st.header("📚 Vault Management")

    # Refresh button
    if st.button("🔄 Refresh"):
        st.rerun()

    # Load vaults
    try:
        vaults = get_vaults()

        if not vaults:
            st.info("No vaults found. Upload a vault to get started.")
            return

        # Create DataFrame
        df = pd.DataFrame(
            [
                {
                    "Name": vault["name"],
                    "Status": vault["status"],
                    "Size": f"{vault['file_size'] / 1024 / 1024:.1f} MB",
                    "Files": vault.get("file_count", 0),
                    "Created": datetime.fromisoformat(
                        vault["created_at"].replace("Z", "+00:00")
                    ).strftime("%Y-%m-%d %H:%M"),
                    "ID": vault["id"],
                }
                for vault in vaults
            ]
        )

        # Display vaults
        st.dataframe(
            df.drop(columns=["ID"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn(
                    "Status", help="Current processing status"
                ),
                "Size": st.column_config.TextColumn("Size", help="File size in MB"),
                "Files": st.column_config.NumberColumn(
                    "Files", help="Number of files in vault"
                ),
            },
        )

        # Vault details
        st.subheader("Vault Details")

        vault_names = {vault["name"]: vault for vault in vaults}
        selected_vault_name = st.selectbox(
            "Select vault for details", options=list(vault_names.keys())
        )

        if selected_vault_name:
            vault = vault_names[selected_vault_name]

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Status", vault["status"])
                st.metric("File Count", vault.get("file_count", 0))
                st.metric("Processed Files", vault.get("processed_files", 0))

            with col2:
                st.metric("Original Filename", vault["original_filename"])
                st.metric("File Size", f"{vault['file_size'] / 1024 / 1024:.1f} MB")

                if vault.get("error_message"):
                    st.error(f"Error: {vault['error_message']}")

            # Delete button
            if st.button(f"🗑️ Delete {vault['name']}", type="secondary"):
                if st.warning(f"Are you sure you want to delete '{vault['name']}'?"):
                    try:
                        delete_vault(vault["id"])
                        st.success("Vault deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Delete failed: {str(e)}")

    except Exception as e:
        st.error(f"Failed to load vaults: {str(e)}")


def analytics_page() -> None:
    """Display the analytics page."""
    st.header("📊 Analytics")

    st.info("Analytics features coming soon!")

    # Placeholder for analytics
    st.subheader("Vault Statistics")

    try:
        vaults = get_vaults()

        if vaults:
            # Basic statistics
            total_vaults = len(vaults)
            total_size = sum(vault["file_size"] for vault in vaults)
            total_files = sum(vault.get("file_count", 0) for vault in vaults)

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Vaults", total_vaults)

            with col2:
                st.metric("Total Size", f"{total_size / 1024 / 1024:.1f} MB")

            with col3:
                st.metric("Total Files", total_files)

            # Status distribution
            st.subheader("Status Distribution")
            status_counts: Dict[str, int] = {}
            for vault in vaults:
                status = vault["status"]
                status_counts[status] = status_counts.get(status, 0) + 1

            if status_counts:
                st.bar_chart(
                    pd.DataFrame(
                        list(status_counts.items()), columns=["Status", "Count"]
                    ).set_index("Status")
                )

    except Exception as e:
        st.error(f"Failed to load analytics: {str(e)}")


def settings_page() -> None:
    """Display the settings page."""
    st.header("⚙️ Settings")

    st.subheader("API Configuration")

    # API Base URL
    api_url = st.text_input(
        "API Base URL",
        value=settings.API_BASE_URL,
        help="Base URL for the SecondBrain API",
    )

    # Connection test
    if st.button("Test Connection"):
        try:
            response = requests.get(f"{api_url}/health", timeout=10)
            if response.status_code == 200:
                st.success("✅ Connection successful!")
            else:
                st.error(f"❌ Connection failed: HTTP {response.status_code}")
        except Exception as e:
            st.error(f"❌ Connection failed: {str(e)}")

    st.subheader("About")
    st.markdown(
        """
    **SecondBrain** is an AI-powered knowledge management system that
    helps you organize, process, and analyze your Obsidian vaults.

    - **Version**: 0.1.0
    - **API**: FastAPI backend with Celery workers
    - **UI**: Streamlit for rapid prototyping
    - **Storage**: PostgreSQL + Redis
    """
    )


def upload_vault(name: str, file: Any) -> Dict[str, Any]:
    """Upload vault to API."""
    files = {"file": (file.name, file, "application/zip")}
    data = {"name": name}

    response = requests.post(
        f"{settings.API_BASE_URL}/api/v1/vaults/upload",
        files=files,
        data=data,
        timeout=60,
    )

    if response.status_code == 200:
        result = response.json()
        return {
            "status": "success",
            "vault_id": result["id"],
            "message": result.get("message", "Upload successful"),
        }
    else:
        return {
            "status": "error",
            "message": f"HTTP {response.status_code}: {response.text}",
        }


def get_vaults() -> List[Dict[str, Any]]:
    """Get list of vaults from API."""
    response = requests.get(f"{settings.API_BASE_URL}/api/v1/vaults/", timeout=10)
    response.raise_for_status()
    return response.json()


def delete_vault(vault_id: str) -> None:
    """Delete vault via API."""
    response = requests.delete(
        f"{settings.API_BASE_URL}/api/v1/vaults/{vault_id}", timeout=10
    )
    response.raise_for_status()


if __name__ == "__main__":
    main()
