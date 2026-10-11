import json
import urllib.request
import urllib.error
from unittest.mock import patch, MagicMock
import importlib.util
import sys
import os

# Load bin/laya-router as a module
spec = importlib.util.spec_from_loader("laya_router", importlib.machinery.SourceFileLoader("laya_router", "bin/laya-router"))
laya_router = importlib.util.module_from_spec(spec)
sys.modules["laya_router"] = laya_router
spec.loader.exec_module(laya_router)

def test_check_health_success():
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"status": "ok"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        
        result = laya_router.check_health()
        assert result == {"status": "ok"}

def test_check_health_failure():
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = Exception("Connection error")
        
        result = laya_router.check_health()
        assert result is None

def test_query_laya_success():
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = json.dumps({"test": "data"}).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        
        result = laya_router.query_laya("prompt", {})
        assert result == {"test": "data"}

def test_query_laya_failure():
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = Exception("Connection error")
        
        result = laya_router.query_laya("prompt", {})
        assert result is None

def test_fast_route_success():
    with patch("laya_router.query_laya") as mock_query:
        mock_query.return_value = {
            "answers": {
                "model_tier": {"choice": "flash_lite"},
                "interaction": {"choice": "qa"}
            }
        }
        
        result = laya_router.fast_route("prompt")
        assert result["status"] == "ok"
        assert result["model_tier"] == "flash_lite"
        assert result["mode"] == "print"
        assert "elapsed_ms" in result

def test_fast_route_fallback():
    with patch("laya_router.query_laya") as mock_query:
        mock_query.return_value = None
        
        result = laya_router.fast_route("prompt")
        assert result["status"] == "fallback"
        assert result["model_tier"] == "flash"
        assert result["mode"] == "interactive"

def test_decide_success():
    with patch("laya_router.query_laya") as mock_query:
        mock_query.return_value = {
            "answers": {
                "model_tier": {"choice": "pro"},
                "interaction": {"choice": "task"},
                "complexity": {"score": 3.0}
            }
        }
        
        result = laya_router.decide("prompt")
        assert result["status"] == "ok"
        assert result["model_tier"] == "pro"
        assert result["mode"] == "interactive"
        assert result["answers"]["complexity"]["score"] == 3.0

def test_decide_fallback():
    with patch("laya_router.query_laya") as mock_query:
        mock_query.return_value = None
        
        result = laya_router.decide("prompt")
        assert result["status"] == "fallback"
        assert result["model_tier"] == "flash"
        assert result["mode"] == "interactive"
        assert "answers" in result

@patch('sys.argv', ['laya-router', 'route', 'test prompt'])
@patch('sys.stdout', new_callable=MagicMock)
def test_main_route(mock_stdout):
    with patch("laya_router.fast_route") as mock_route:
        mock_route.return_value = {
            "status": "ok",
            "model_tier": "flash_lite",
            "mode": "print",
            "elapsed_ms": 100
        }
        try:
            laya_router.main()
        except SystemExit as e:
            assert e.code == 0
            # Test that it prints the expected output format
            # In the new code, fast_route returns dict, then print(f"{res['model_tier']} {res['mode']}")
            assert mock_stdout.write.call_args_list[0][0][0].strip() == "flash_lite print"

@patch('sys.argv', ['laya-router', 'tier', 'test prompt'])
@patch('sys.stdout', new_callable=MagicMock)
def test_main_tier(mock_stdout):
    with patch("laya_router.fast_route") as mock_route:
        mock_route.return_value = {
            "status": "ok",
            "model_tier": "pro",
            "mode": "interactive",
            "elapsed_ms": 100
        }
        try:
            laya_router.main()
        except SystemExit as e:
            assert e.code == 0
            assert mock_stdout.write.call_args_list[0][0][0].strip() == "pro"

@patch('sys.argv', ['laya-router', 'health'])
@patch('sys.stdout', new_callable=MagicMock)
def test_main_health_success(mock_stdout):
    with patch("laya_router.check_health") as mock_health:
        mock_health.return_value = {"status": "ok"}
        try:
            laya_router.main()
        except SystemExit as e:
            assert e.code == 0

@patch('sys.argv', ['laya-router', 'health'])
@patch('sys.stdout', new_callable=MagicMock)
def test_main_health_failure(mock_stdout):
    with patch("laya_router.check_health") as mock_health:
        mock_health.return_value = None
        try:
            laya_router.main()
        except SystemExit as e:
            assert e.code == 1

