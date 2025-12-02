import os
from typing import Optional, List

import requests
import streamlit as st


# ------------------------------
# Config
# ------------------------------

def get_backend_base_url() -> str:
    # Default for local dev; can be overridden by env or UI input
    return os.getenv("BACKEND_BASE_URL", "http://localhost:8000")


# ------------------------------
# API client helpers
# ------------------------------

class BackendClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    # --- Workspaces ---

    def list_workspaces(self) -> List[dict]:
        resp = requests.get(f"{self.base_url}/api/v1/workspaces")
        resp.raise_for_status()
        return resp.json()

    def create_workspace(self, name: str, description: Optional[str]) -> dict:
        payload = {"name": name, "description": description}
        resp = requests.post(f"{self.base_url}/api/v1/workspaces", json=payload)
        resp.raise_for_status()
        return resp.json()

    # --- Knowledge bases ---

    def list_kbs(self, workspace_id: str) -> List[dict]:
        resp = requests.get(f"{self.base_url}/api/v1/workspaces/{workspace_id}/knowledge-bases")
        resp.raise_for_status()
        return resp.json()

    def create_kb(self, workspace_id: str, name: str, description: Optional[str]) -> dict:
        payload = {"name": name, "description": description}
        resp = requests.post(
            f"{self.base_url}/api/v1/workspaces/{workspace_id}/knowledge-bases",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    # --- Collections ---

    def list_collections(self, kb_id: str) -> List[dict]:
        resp = requests.get(f"{self.base_url}/api/v1/knowledge-bases/{kb_id}/collections")
        resp.raise_for_status()
        return resp.json()

    def create_collection(self, kb_id: str, name: str, description: Optional[str]) -> dict:
        payload = {"name": name, "description": description}
        resp = requests.post(
            f"{self.base_url}/api/v1/knowledge-bases/{kb_id}/collections",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()

    # --- Documents ---

    def list_documents(self, collection_id: str) -> List[dict]:
        resp = requests.get(f"{self.base_url}/api/v1/collections/{collection_id}/documents")
        resp.raise_for_status()
        return resp.json()

    def upload_document(self, collection_id: str, file) -> dict:
        files = {"file": (file.name, file.read(), file.type)}
        resp = requests.post(
            f"{self.base_url}/api/v1/collections/{collection_id}/documents",
            files=files,
        )
        resp.raise_for_status()
        return resp.json()

    # --- Datasets ---

    def list_datasets(self, workspace_id: str) -> List[dict]:
        resp = requests.get(f"{self.base_url}/api/v1/workspaces/{workspace_id}/datasets")
        resp.raise_for_status()
        return resp.json()

    def upload_dataset(self, workspace_id: str, name: str, file) -> dict:
        data = {"name": name}
        files = {"file": (file.name, file.read(), file.type)}
        resp = requests.post(
            f"{self.base_url}/api/v1/workspaces/{workspace_id}/datasets",
            data=data,
            files=files,
        )
        resp.raise_for_status()
        return resp.json()


# ------------------------------
# UI helpers
# ------------------------------

def ensure_session_state():
    if "backend_url" not in st.session_state:
        st.session_state.backend_url = get_backend_base_url()
    if "selected_workspace_id" not in st.session_state:
        st.session_state.selected_workspace_id = None
    if "selected_kb_id" not in st.session_state:
        st.session_state.selected_kb_id = None
    if "selected_collection_id" not in st.session_state:
        st.session_state.selected_collection_id = None


def select_workspace(client: BackendClient):
    st.subheader("Workspaces")

    workspaces = client.list_workspaces()
    workspace_options = {w["name"]: w for w in workspaces}

    cols = st.columns([3, 2])
    with cols[0]:
        if workspace_options:
            names = list(workspace_options.keys())
            default_index = 0
            if st.session_state.selected_workspace_id:
                # Try to keep previously selected workspace highlighted
                for i, w_name in enumerate(names):
                    if workspace_options[w_name]["id"] == st.session_state.selected_workspace_id:
                        default_index = i
                        break
            selected_name = st.selectbox("Select workspace", names, index=default_index)
            selected_ws = workspace_options[selected_name]
            st.session_state.selected_workspace_id = selected_ws["id"]
            st.caption(f"Selected workspace ID: {selected_ws['id']}")
        else:
            st.info("No workspaces yet. Create one below.")

    with cols[1]:
        with st.expander("Create workspace", expanded=not workspace_options):
            with st.form("create_workspace_form"):
                name = st.text_input("Name", "")
                desc = st.text_area("Description", "", height=80)
                submitted = st.form_submit_button("Create")
                if submitted:
                    if not name.strip():
                        st.error("Workspace name is required.")
                    else:
                        try:
                            created = client.create_workspace(name=name.strip(), description=desc or None)
                            st.success(f"Workspace created: {created['name']}")
                            st.session_state.selected_workspace_id = created["id"]
                            st.experimental_rerun()
                        except requests.HTTPError as e:
                            st.error(f"Error creating workspace: {e.response.text}")


def knowledge_bases_view(client: BackendClient):
    st.header("Knowledge Bases")

    ws_id = st.session_state.selected_workspace_id
    if not ws_id:
        st.warning("Select a workspace first in the sidebar.")
        return

    # List KBs
    try:
        kbs = client.list_kbs(ws_id)
    except requests.HTTPError as e:
        st.error(f"Error listing knowledge bases: {e.response.text}")
        return

    if kbs:
        kb_map = {kb["name"]: kb for kb in kbs}
        names = list(kb_map.keys())
        default_idx = 0
        if st.session_state.selected_kb_id:
            for i, name in enumerate(names):
                if kb_map[name]["id"] == st.session_state.selected_kb_id:
                    default_idx = i
                    break
        selected_name = st.selectbox("Select knowledge base", names, index=default_idx)
        selected_kb = kb_map[selected_name]
        st.session_state.selected_kb_id = selected_kb["id"]
        st.caption(f"Selected KB ID: {selected_kb['id']}")
    else:
        st.info("No knowledge bases in this workspace yet.")

    # Create KB form
    with st.expander("Create knowledge base", expanded=not kbs):
        with st.form("create_kb_form"):
            name = st.text_input("KB name", "")
            desc = st.text_area("Description", "", height=80)
            submitted = st.form_submit_button("Create")
            if submitted:
                if not name.strip():
                    st.error("KB name is required.")
                else:
                    try:
                        created = client.create_kb(ws_id, name=name.strip(), description=desc or None)
                        st.success(f"Knowledge base created: {created['name']}")
                        st.session_state.selected_kb_id = created["id"]
                        st.experimental_rerun()
                    except requests.HTTPError as e:
                        st.error(f"Error creating knowledge base: {e.response.text}")


def collections_and_documents_view(client: BackendClient):
    st.header("Collections & Documents")

    ws_id = st.session_state.selected_workspace_id
    if not ws_id:
        st.warning("Select a workspace first in the sidebar.")
        return

    kb_id = st.session_state.selected_kb_id
    if not kb_id:
        st.warning("Select a knowledge base in the 'Knowledge Bases' tab first.")
        return

    # List collections
    try:
        collections = client.list_collections(kb_id)
    except requests.HTTPError as e:
        st.error(f"Error listing collections: {e.response.text}")
        return

    cols = st.columns([3, 2])

    with cols[0]:
        if collections:
            col_map = {c["name"]: c for c in collections}
            names = list(col_map.keys())
            default_idx = 0
            if st.session_state.selected_collection_id:
                for i, name in enumerate(names):
                    if col_map[name]["id"] == st.session_state.selected_collection_id:
                        default_idx = i
                        break
            selected_name = st.selectbox("Select collection", names, index=default_idx)
            selected_collection = col_map[selected_name]
            st.session_state.selected_collection_id = selected_collection["id"]
            st.caption(f"Selected collection ID: {selected_collection['id']}")
        else:
            st.info("No collections in this knowledge base yet.")

    with cols[1]:
        with st.expander("Create collection", expanded=not collections):
            with st.form("create_collection_form"):
                name = st.text_input("Collection name", "")
                desc = st.text_area("Description", "", height=80)
                submitted = st.form_submit_button("Create")
                if submitted:
                    if not name.strip():
                        st.error("Collection name is required.")
                    else:
                        try:
                            created = client.create_collection(kb_id, name=name.strip(), description=desc or None)
                            st.success(f"Collection created: {created['name']}")
                            st.session_state.selected_collection_id = created["id"]
                            st.experimental_rerun()
                        except requests.HTTPError as e:
                            st.error(f"Error creating collection: {e.response.text}")

    # Documents area
    collection_id = st.session_state.selected_collection_id
    if not collection_id:
        return

    st.subheader("Documents")
    col1, col2 = st.columns([2, 3])

    with col1:
        uploaded_file = st.file_uploader("Upload document", type=None)
        if uploaded_file is not None:
            if st.button("Upload document"):
                try:
                    created = client.upload_document(collection_id, uploaded_file)
                    st.success(f"Uploaded: {created['filename']} ({created['size_bytes']} bytes)")
                    st.experimental_rerun()
                except requests.HTTPError as e:
                    st.error(f"Error uploading document: {e.response.text}")

    with col2:
        try:
            docs = client.list_documents(collection_id)
        except requests.HTTPError as e:
            st.error(f"Error listing documents: {e.response.text}")
            return

        if docs:
            st.write("Documents in this collection:")
            for doc in docs:
                st.markdown(
                    f"- **{doc['filename']}** "
                    f"({doc['size_bytes']} bytes, status: `{doc['status']}`)"
                )
        else:
            st.info("No documents uploaded yet.")


def datasets_view(client: BackendClient):
    st.header("Datasets")

    ws_id = st.session_state.selected_workspace_id
    if not ws_id:
        st.warning("Select a workspace first in the sidebar.")
        return

    # Upload new dataset
    with st.expander("Upload dataset (CSV)", expanded=True):
        with st.form("upload_dataset_form"):
            name = st.text_input("Dataset name", "")
            file = st.file_uploader("CSV file", type=["csv"])
            submitted = st.form_submit_button("Upload")
            if submitted:
                if not name.strip():
                    st.error("Dataset name is required.")
                elif file is None:
                    st.error("CSV file is required.")
                else:
                    try:
                        created = client.upload_dataset(ws_id, name=name.strip(), file=file)
                        st.success(f"Dataset uploaded: {created['name']} ({created['filename']})")
                        st.experimental_rerun()
                    except requests.HTTPError as e:
                        st.error(f"Error uploading dataset: {e.response.text}")

    # List datasets
    try:
        datasets = client.list_datasets(ws_id)
    except requests.HTTPError as e:
        st.error(f"Error listing datasets: {e.response.text}")
        return

    if datasets:
        st.subheader("Existing datasets")
        for ds in datasets:
            st.markdown(
                f"- **{ds['name']}** ({ds['filename']}) – "
                f"{ds['size_bytes']} bytes, ID: `{ds['id']}`"
            )
    else:
        st.info("No datasets for this workspace yet.")


# ------------------------------
# Main app
# ------------------------------

def main():
    ensure_session_state()

    st.set_page_config(
        page_title="Yaya AI Lab",
        layout="wide",
    )

    st.title("Yaya AI Lab – Admin UI")

    # Sidebar: backend URL + workspace selection
    with st.sidebar:
        st.markdown("### Backend configuration")

        backend_url = st.text_input(
            "Backend base URL",
            value=st.session_state.backend_url,
            help="FastAPI base URL, e.g. http://localhost:8000",
        )
        st.session_state.backend_url = backend_url
        client = BackendClient(backend_url)

        st.markdown("---")
        select_workspace(client)

    # Main tabs
    tab_kb, tab_col_docs, tab_datasets = st.tabs(
        ["Knowledge Bases", "Collections & Documents", "Datasets"]
    )

    with tab_kb:
        knowledge_bases_view(client)

    with tab_col_docs:
        collections_and_documents_view(client)

    with tab_datasets:
        datasets_view(client)


if __name__ == "__main__":
    main()
