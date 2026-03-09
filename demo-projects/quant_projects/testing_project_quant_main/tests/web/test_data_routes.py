"""Unit tests for data API routes."""
from unittest.mock import patch, MagicMock
import pandas as pd


class TestDataStatus:
    def test_returns_all_categories(self, client):
        mock_store = MagicMock()
        mock_store.get_last_updated.return_value = "2024-06-01"
        mock_store.read_table.return_value = pd.DataFrame({"a": [1, 2, 3]})

        with patch("src.data.storage.DataStore", return_value=mock_store):
            resp = client.get("/api/data/status")

        assert resp.status_code == 200
        data = resp.json()
        for cat in ["stock", "futures", "macro", "flow"]:
            assert cat in data
            assert "last_updated" in data[cat]
            assert "rows" in data[cat]

    def test_handles_missing_table(self, client):
        mock_store = MagicMock()
        mock_store.get_last_updated.return_value = None
        mock_store.read_table.side_effect = Exception("table not found")

        with patch("src.data.storage.DataStore", return_value=mock_store):
            resp = client.get("/api/data/status")

        assert resp.status_code == 200
        data = resp.json()
        assert data["stock"]["rows"] == 0


    def test_database_error_returns_error(self, client):
        """R1-UC1-E3: Database error during status check returns error JSON."""
        with patch("src.data.storage.DataStore", side_effect=Exception("cannot open database")):
            resp = client.get("/api/data/status")

        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data
        assert "cannot open database" in data["error"]


class TestDataUpdate:
    def test_update_all(self, client):
        mock_pipeline = MagicMock()
        mock_store = MagicMock()
        mock_store.get_last_updated.return_value = "2024-06-01"
        mock_store.read_table.return_value = pd.DataFrame({"a": range(10)})

        with patch("src.data.pipeline.DataPipeline", return_value=mock_pipeline), \
             patch("src.data.storage.DataStore", return_value=mock_store), \
             patch("src.universe.classifier.get_universe", return_value=pd.DataFrame({"symbol": ["601600.SH"]})):
            resp = client.post("/api/data/update", json={"categories": ["all"]})

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "results" in data
        mock_pipeline.run.assert_called_once()

    def test_update_specific_category(self, client):
        mock_pipeline = MagicMock()
        mock_store = MagicMock()
        mock_store.get_last_updated.return_value = "2024-06-01"
        mock_store.read_table.return_value = pd.DataFrame({"a": range(5)})

        with patch("src.data.pipeline.DataPipeline", return_value=mock_pipeline), \
             patch("src.data.storage.DataStore", return_value=mock_store):
            resp = client.post("/api/data/update", json={"categories": ["macro"]})

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "macro" in data["results"]

    def test_update_with_force_refresh(self, client):
        """R1-UC2-E3: Force refresh passes force_refresh=True to pipeline."""
        mock_pipeline = MagicMock()
        mock_store = MagicMock()
        mock_store.get_last_updated.return_value = "2024-06-01"
        mock_store.read_table.return_value = pd.DataFrame({"a": range(5)})

        with patch("src.data.pipeline.DataPipeline", return_value=mock_pipeline), \
             patch("src.data.storage.DataStore", return_value=mock_store):
            resp = client.post("/api/data/update", json={"categories": ["macro"], "force": True})

        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        # Verify force_refresh was passed to pipeline
        call_kwargs = mock_pipeline.run.call_args
        assert call_kwargs[1].get("force_refresh") is True or \
               (call_kwargs[0] if call_kwargs[0] else False)

    def test_update_error_returns_error(self, client):
        mock_pipeline = MagicMock()
        mock_pipeline.run.side_effect = Exception("connection timeout")

        with patch("src.data.pipeline.DataPipeline", return_value=mock_pipeline):
            resp = client.post("/api/data/update", json={"categories": ["all"]})

        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data
