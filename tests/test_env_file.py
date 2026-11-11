import os

from app import load_env_file


def test_env_file_is_read_but_does_not_overwrite(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text("# comment\nOPENAI_API_KEY=sk-test\nOTHER=\"quoted\"\nKEEP=new\n")
    # setenv first, so pytest puts the variables back to "not set" after the test
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("OTHER", "x")
    monkeypatch.delenv("OPENAI_API_KEY")
    monkeypatch.delenv("OTHER")
    monkeypatch.setenv("KEEP", "old")
    load_env_file(str(env))
    assert os.environ["OPENAI_API_KEY"] == "sk-test"
    assert os.environ["OTHER"] == "quoted"
    assert os.environ["KEEP"] == "old"


def test_missing_env_file_is_fine(tmp_path):
    load_env_file(str(tmp_path / "nothing.env"))
