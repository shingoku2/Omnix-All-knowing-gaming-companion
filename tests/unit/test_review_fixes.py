"""Regression tests for defects found in the 2026-10 code review."""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, Mock

import pytest

import omnix.config as config_mod
from omnix.credential_store import CredentialStore, KeyringUnavailableError
from omnix.keybind_manager import KeybindManager, MacroKeybind
from omnix.knowledge_index import KnowledgeIndex, SimpleTFIDFEmbedding
from omnix.knowledge_pack import KnowledgePack, KnowledgeSource
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
