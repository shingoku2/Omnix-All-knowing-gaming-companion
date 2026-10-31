"""Regression tests for defects found in the 2026-10 code review."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock

import pytest

import omnix.config as config_mod
from omnix.credential_store import CredentialStore, KeyringUnavailableError
from omnix.keybind_manager import Keybind, KeybindManager, MacroKeybind
from omnix.knowledge_index import KnowledgeIndex, SimpleTFIDFEmbedding
from omnix.knowledge_pack import KnowledgePack, KnowledgeSource
from omnix.knowledge_packs_tab import IngestionWorker
from omnix.licensing import get_installation_id
from omnix.macro_manager import Macro, MacroStep, MacroStepType
from omnix.macro_runner import MacroExecutionState, MacroRunner
from omnix.providers import OllamaProvider
from omnix.session_logger import SessionLogger


@pytest.mark.unit
def test_vault_not_quarantined_when_key_unavailable(temp_config_dir, monkeypatch):
    store = CredentialStore(base_dir=temp_config_dir, allow_password_prompt=False)
    store.save_credentials({"AI_API_KEY": "secret"})
    vault = store.credential_path

    def no_key():
        raise KeyringUnavailableError("no keyring and no master password")

    monkeypatch.setattr(store, "_get_cipher", no_key)
    assert store.get("AI_API_KEY") is None
    assert vault.exists(), "vault must stay in place for a later run that has the key"


@pytest.mark.unit
def test_save_to_env_keeps_unmanaged_keys_and_new_values(tmp_path, monkeypatch):
    monkeypatch.setattr(config_mod, "__file__", str(tmp_path / "omnix" / "config.py"))
    env_file = tmp_path / ".env"
    env_file.write_text(
        "OLLAMA_HOST=http://old:11434\n"
        "OVERLAY_HOTKEY=ctrl+shift+g\n"
        "CHECK_INTERVAL=5\n"
        "SUPABASE_URL=https://example.supabase.co\n"
        "MACROS_ENABLED=true\n",
        encoding="utf-8",
    )

    config_mod.Config.save_to_env(overlay_hotkey="ctrl+alt+o", check_interval=9)

    saved = env_file.read_text(encoding="utf-8")
    assert "OVERLAY_HOTKEY=ctrl+alt+o" in saved
    assert "CHECK_INTERVAL=9" in saved
    assert "OLLAMA_HOST=http://old:11434" in saved
    assert "SUPABASE_URL=https://example.supabase.co" in saved
    assert "MACROS_ENABLED=true" in saved


@pytest.mark.unit
class TestSessionLoggerFixes:
    def test_session_file_keeps_more_than_100_events(self, temp_config_dir):
        logger = SessionLogger(config_dir=temp_config_dir)
        for i in range(150):
            logger.log_event("game", "question", f"q{i}")

        session_id = logger.current_sessions["game"]
        assert len(logger._load_session("game", session_id)) == 150

    def test_new_session_starts_with_empty_buffer(self, temp_config_dir):
        logger = SessionLogger(config_dir=temp_config_dir)
        logger.log_event("game", "question", "old session")
        logger.last_event_time["game"] = datetime.now() - timedelta(hours=3)
        logger.current_sessions["game"] = "20000101_000000"

        logger.log_event("game", "question", "new session")

        contents = [e.content for e in logger.get_current_session_events("game")]
        assert contents == ["new session"]

    def test_profile_prefix_does_not_match_other_profiles(self, temp_config_dir):
        logger = SessionLogger(config_dir=temp_config_dir)
        logger.log_event("elden_ring", "question", "q")

        assert logger._session_files("elden") == []
        assert len(logger._session_files("elden_ring")) == 1


def _pack(pack_id, content):
    return KnowledgePack(
        id=pack_id,
        name=pack_id,
        description="",
        game_profile_id="game",
        sources=[KnowledgeSource(id=f"{pack_id}-src", type="file", title="guide", content=content)],
    )


@pytest.mark.unit
class TestKnowledgeIndexFixes:
    def test_idf_is_positive_on_small_corpus(self):
        embedding = SimpleTFIDFEmbedding()
        embedding.fit(["boss weak to fire", "use frost on dragons"])
        assert all(value > 0 for value in embedding.idf.values())

    def test_add_pack_indexes_in_memory_content(self, tmp_path):
        stored = _pack("p1", None)  # Saved copy has no content yet
        store = Mock()
        store.get_packs_for_game.return_value = {"p1": stored}
        index = KnowledgeIndex(
            config_dir=str(tmp_path),
            embedding_provider=SimpleTFIDFEmbedding(),
            knowledge_store=store,
        )

        index.add_pack(_pack("p1", "The fire giant is weak to frost magic."))

        assert index.index["game"], "freshly ingested content must be indexed"

    def test_remove_pack_does_not_reindex_removed_pack(self, tmp_path):
        pack = _pack("p1", "The fire giant is weak to frost magic.")
        store = Mock()
        store.get_packs_for_game.return_value = {"p1": pack}
        index = KnowledgeIndex(
            config_dir=str(tmp_path),
            embedding_provider=SimpleTFIDFEmbedding(),
            knowledge_store=store,
        )
        index.add_pack(pack)

        index.remove_pack("p1")  # Store still holds it, as in the real delete flow

        assert not index.index.get("game")


@pytest.mark.unit
def test_ollama_list_models_reads_model_field():
    provider = OllamaProvider.__new__(OllamaProvider)
    provider.base_url = "http://localhost:11434"
    provider.client = MagicMock()
    provider.client.list.return_value = {"models": [{"model": "llama3:8b"}]}
    provider.is_configured = lambda: True

    assert provider.list_models() == ["llama3:8b"]


@pytest.mark.unit
class TestMacroRunnerFixes:
    def _runner(self):
        runner = MacroRunner(enabled=True, capabilities=Mock(automation_available=True))
        runner.keyboard_controller = MagicMock()
        runner.mouse_controller = MagicMock()
        runner._parse_key_combo = lambda combo: [combo]
        return runner

    def test_stop_releases_keys_held_by_key_down(self):
        runner = self._runner()
        macro = Macro(
            id="m",
            name="hold",
            description="",
            steps=[
                MacroStep(type=MacroStepType.KEY_DOWN.value, key="w", duration_ms=0),
                MacroStep(type=MacroStepType.DELAY.value, duration_ms=3000),
                MacroStep(type=MacroStepType.KEY_UP.value, key="w"),
            ],
        )
        assert runner.execute_macro(macro)
        deadline = datetime.now() + timedelta(seconds=2)
        while not runner.keyboard_controller.press.called and datetime.now() < deadline:
            pass
        runner.stop_macro()
        runner.execution_thread.join(timeout=2)

        runner.keyboard_controller.release.assert_any_call("w")
        assert runner.state == MacroExecutionState.STOPPED

    def test_stop_works_while_paused(self):
        runner = self._runner()
        runner.state = MacroExecutionState.PAUSED
        runner.stop_macro()
        assert runner.state == MacroExecutionState.STOPPED


@pytest.mark.unit
def test_macro_keybind_can_be_reregistered_without_override():
    manager = KeybindManager(Mock(global_hotkeys=False))
    keybind = MacroKeybind(macro_id="heal", keys="ctrl+h", description="Heal")

    assert manager.register_macro_keybind(keybind, lambda: None)
    assert manager.register_macro_keybind(keybind, lambda: None)


@pytest.mark.unit
def test_failed_macro_rebind_keeps_previous_binding():
    manager = KeybindManager(Mock(global_hotkeys=False))
    manager.register_keybind(
        Keybind(action="toggle", keys="ctrl+j", description="t", system_wide=False), lambda: None
    )
    original = MacroKeybind(macro_id="heal", keys="ctrl+h", description="Heal", game_profile_id="g")
    assert manager.register_macro_keybind(original, lambda: None)

    clash = MacroKeybind(macro_id="heal", keys="ctrl+j", description="Heal", game_profile_id="g")
    assert not manager.register_macro_keybind(clash, lambda: None)
    assert manager.macro_keybinds["heal"].keys == "ctrl+h"


@pytest.mark.unit
def test_save_to_env_rejects_line_breaks(tmp_path, monkeypatch):
    monkeypatch.setattr(config_mod, "__file__", str(tmp_path / "omnix" / "config.py"))
    env_file = tmp_path / ".env"
    env_file.write_text("OLLAMA_HOST=http://old:11434\n", encoding="utf-8")

    with pytest.raises(ValueError):
        config_mod.Config.save_to_env(ollama_host="http://x\nOLLAMA_HOST=http://evil")
    assert env_file.read_text(encoding="utf-8") == "OLLAMA_HOST=http://old:11434\n"


@pytest.mark.unit
def test_installation_id_stable_when_vault_unwritable():
    store = Mock()
    store.get_credential.return_value = None
    store.set_credential.side_effect = RuntimeError("vault unavailable")

    assert get_installation_id(store) == get_installation_id(store)


def _worker(pack, save_ok=True, ingest_error=None):
    from omnix.knowledge_ingestion import IngestionError

    index = Mock()
    index.knowledge_store.save_pack.return_value = save_ok
    worker = IngestionWorker(pack, index)
    worker.pipeline = Mock()
    if ingest_error:
        worker.pipeline.ingest.side_effect = IngestionError(ingest_error)
    else:
        worker.pipeline.ingest.return_value = "guide text"
    results = []
    worker.finished.connect(lambda ok, msg: results.append((ok, msg)))
    worker.run()
    return worker, index, results


@pytest.mark.unit
class TestIngestionWorkerFixes:
    def test_saves_through_index_store(self, qapp):
        _, index, results = _worker(_pack("p1", None))
        index.knowledge_store.save_pack.assert_called_once()
        assert results == [(True, "Successfully indexed 1 sources")]

    def test_failed_save_is_reported_as_failure(self, qapp):
        _, index, results = _worker(_pack("p1", None), save_ok=False)
        index.add_pack.assert_not_called()
        assert results[0][0] is False

    def test_failed_source_is_not_reported_as_success(self, qapp):
        _, _, results = _worker(_pack("p1", None), ingest_error="404")
        assert results[0][0] is False
        assert "guide" in results[0][1]


@pytest.mark.unit
def test_legacy_idf_index_is_reembedded_on_load(tmp_path):
    store = Mock()
    store.get_packs_for_game.return_value = {}
    index = KnowledgeIndex(
        config_dir=str(tmp_path), embedding_provider=SimpleTFIDFEmbedding(), knowledge_store=store
    )
    provider = index.embedding_provider
    provider.fit(["boss weak to fire", "use frost on dragons"])
    provider.idf = {token: 0.0 for token in provider.idf}  # Legacy formula output
    index.index = {"game": {"c1": ("boss weak to fire", "s", "p", [0.0] * 7, {})}}

    index._refit_legacy_idf()

    assert min(provider.idf.values()) >= 1
    assert any(index.index["game"]["c1"][3])


@pytest.mark.unit
def test_save_migrates_legacy_json_api_key_into_vault(tmp_path, monkeypatch):
    monkeypatch.delenv("AI_API_KEY", raising=False)
    config_path = tmp_path / "config.json"
    config_path.write_text('{"ai_api_key": "legacy-key"}', encoding="utf-8")

    config = config_mod.Config(require_keys=False, config_path=str(config_path))
    assert config.ai_api_key == "legacy-key"
    assert config.save()

    assert "legacy-key" not in config_path.read_text(encoding="utf-8")
    reloaded = config_mod.Config(require_keys=False, config_path=str(config_path))
    assert reloaded.ai_api_key == "legacy-key"


@pytest.mark.unit
class TestIngestionRefresh:
    def test_reindex_refetches_cached_file_content(self, qapp):
        pack = _pack("p1", "old guide text")
        worker, _, results = _worker(pack)  # pipeline returns "guide text"
        worker.pipeline.ingest.assert_called_once()
        assert pack.sources[0].content == "guide text"
        assert results[0][0] is True

    def test_failed_refetch_keeps_previous_content(self, qapp):
        pack = _pack("p1", "old guide text")
        _, _, results = _worker(pack, ingest_error="offline")
        assert pack.sources[0].content == "old guide text"
        assert results[0][0] is False


@pytest.mark.unit
def test_pause_does_not_outlive_macro_timeout():
    runner = TestMacroRunnerFixes()._runner()
    macro = Macro(
        id="m",
        name="hold",
        description="",
        execution_timeout=0.3,
        steps=[
            MacroStep(type=MacroStepType.KEY_DOWN.value, key="w", duration_ms=0),
            MacroStep(type=MacroStepType.KEY_UP.value, key="w"),
        ],
    )
    runner.on_step_executed = lambda done, total: done == 1 and runner.pause_macro()

    assert runner.execute_macro(macro)
    if runner.execution_thread:
        runner.execution_thread.join(timeout=3)

    assert runner.state == MacroExecutionState.ERROR
    runner.keyboard_controller.release.assert_any_call("w")


@pytest.mark.unit
class TestConfigSaveDefaultPath:
    """Config.save() used to be a no-op because config_path was never set."""

    def test_default_config_saves_and_reloads(self, tmp_path):
        config = config_mod.Config(require_keys=False, config_dir=str(tmp_path))
        assert config.config_path == str(tmp_path / "config.json")

        config.overlay_x = 640
        config.ollama_model = "mistral"
        assert config.save()

        reloaded = config_mod.Config(require_keys=False, config_dir=str(tmp_path))
        assert reloaded.overlay_x == 640
        assert reloaded.ollama_model == "mistral"

    def test_save_keeps_unmanaged_keys_and_drops_plaintext_key(self, tmp_path):
        import json

        path = tmp_path / "config.json"
        path.write_text(
            json.dumps({"schema_version": 3, "settings_version": 1, "ai_api_key": "k"}),
            encoding="utf-8",
        )
        config = config_mod.Config(require_keys=False, config_dir=str(tmp_path))
        assert config.save()

        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["schema_version"] == 3
        assert data["settings_version"] == config_mod.SETTINGS_VERSION
        assert "ai_api_key" not in data

    def test_legacy_file_does_not_override_settings(self, tmp_path, monkeypatch):
        monkeypatch.setenv("OLLAMA_MODEL", "from-env")
        baseline = config_mod.Config(require_keys=False, config_dir=str(tmp_path))
        (tmp_path / "config.json").write_text(
            '{"ollama_model": "stale-2x-model", "overlay_x": 7}', encoding="utf-8"
        )
        config = config_mod.Config(require_keys=False, config_dir=str(tmp_path))
        assert config.ollama_model == "from-env"
        assert config.overlay_x == baseline.overlay_x

    def test_invalid_values_are_ignored(self, tmp_path):
        # Other tests leave .env values in os.environ, so compare to a baseline.
        baseline = config_mod.Config(require_keys=False, config_dir=str(tmp_path))
        (tmp_path / "config.json").write_text(
            '{"settings_version": 1, "overlay_x": "left", "check_interval": true,'
            ' "overlay_opacity": 4, "config_dir": "/etc", "overlay_y": 42}',
            encoding="utf-8",
        )
        config = config_mod.Config(require_keys=False, config_dir=str(tmp_path))
        assert config.overlay_x == baseline.overlay_x
        assert config.check_interval == baseline.check_interval
        assert config.overlay_opacity == 1.0
        assert config.config_dir == str(tmp_path)
        assert config.overlay_y == 42

    def test_providers_tab_save_updates_config_json(self, qapp, tmp_path, monkeypatch):
        from omnix import providers_tab

        monkeypatch.setattr(providers_tab.ProvidersTab, "refresh_models", lambda self: None)
        monkeypatch.setattr(providers_tab.Config, "save_to_env", staticmethod(lambda **_: None))
        config = config_mod.Config(require_keys=False, config_dir=str(tmp_path))
        tab = providers_tab.ProvidersTab(config)
        tab.host_input.setText("http://gpu-box:11434")
        assert tab.save_provider_config()

        reloaded = config_mod.Config(require_keys=False, config_dir=str(tmp_path))
        assert reloaded.ollama_host == "http://gpu-box:11434"


@pytest.mark.unit
def test_repeated_save_does_not_rewrite_unchanged_vault_key(tmp_path, monkeypatch):
    monkeypatch.delenv("AI_API_KEY", raising=False)
    config = config_mod.Config(require_keys=False, config_dir=str(tmp_path))
    config.ai_api_key = "k1"
    writes = []
    original = config.credential_store.save_credentials
    monkeypatch.setattr(
        config.credential_store,
        "save_credentials",
        lambda creds: (writes.append(creds), original(creds))[1],
    )

    assert config.save() and config.save()  # e.g. two overlay drags
    assert writes == [{"AI_API_KEY": "k1"}]
    config.ai_api_key = "k2"
    assert config.save()
    assert writes[-1] == {"AI_API_KEY": "k2"}
