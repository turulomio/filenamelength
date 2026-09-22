import json
import os
import tempfile
import pytest
from unittest.mock import patch
from filenamelength.filenamelength import (
    get_user_config_dir,
    ensure_user_config,
    get_config,
    load_history,
    save_history,
    generate_optimized_filename,
    rename_files,
    undo_rename,
    create_lod_files,
    print_lod_files,
    main,
)
from filenamelength.filesystems import get_fsinfo_lod


@pytest.fixture
def temp_config_dir(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_dir))
    return config_dir


class TestConfigManagement:
    def test_get_user_config_dir(self, temp_config_dir):
        d = get_user_config_dir()
        assert str(temp_config_dir) in d
        assert os.path.exists(d)

    def test_ensure_user_config_creates_files(self, temp_config_dir):
        ensure_user_config()
        config_path = os.path.join(get_user_config_dir(), "config.json")
        history_path = os.path.join(get_user_config_dir(), "history.json")
        assert os.path.exists(config_path)
        assert os.path.exists(history_path)

        with open(config_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            assert cfg["max_history_entries"] == 100

        with open(history_path, "r", encoding="utf-8") as f:
            hist = json.load(f)
            assert hist == []

    def test_get_config_and_history(self, temp_config_dir):
        ensure_user_config()
        cfg = get_config()
        assert cfg["max_history_entries"] == 100

        history = load_history()
        assert history == []

        test_history = [{"timestamp": "2026-01-01", "operations": []}]
        save_history(test_history)
        assert load_history() == test_history

    def test_save_history_max_entries(self, temp_config_dir):
        ensure_user_config()
        config_path = os.path.join(get_user_config_dir(), "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump({"max_history_entries": 3}, f)

        items = [{"id": i} for i in range(10)]
        save_history(items)
        loaded = load_history()
        assert len(loaded) == 3
        assert loaded == [{"id": 7}, {"id": 8}, {"id": 9}]


class TestGenerateOptimizedFilename:
    def test_no_change_if_short_enough(self):
        res = generate_optimized_filename("short.txt", 15, set())
        assert res == "short.txt"

    def test_truncation_preserves_extension(self):
        filename = "very_long_file_name_for_testing.pdf"
        target_len = 15
        res = generate_optimized_filename(filename, target_len, set())
        assert len(res) == target_len
        assert res.endswith(".pdf")
        assert res == "very_long_f.pdf"

    def test_collision_appends_number(self):
        filename = "very_long_file_name_for_testing.pdf"
        target_len = 15
        existing = {"very_long_f.pdf"}
        res = generate_optimized_filename(filename, target_len, existing)
        assert len(res) == target_len
        assert res == "very_long_1.pdf"
        assert res not in existing

    def test_multiple_collisions(self):
        filename = "very_long_file_name_for_testing.pdf"
        target_len = 15
        existing = {"very_long_f.pdf", "very_long_1.pdf", "very_long_2.pdf"}
        res = generate_optimized_filename(filename, target_len, existing)
        assert len(res) == target_len
        assert res == "very_long_3.pdf"

    def test_collision_with_two_digit_counter(self):
        filename = "very_long_file_name_for_testing.pdf"
        target_len = 15
        existing = {"very_long_f.pdf"}
        for i in range(1, 10):
            existing.add(f"very_long_{i}.pdf")
        res = generate_optimized_filename(filename, target_len, existing)
        assert len(res) == target_len
        assert res == "very_lon_10.pdf"

    def test_filename_without_extension(self):
        filename = "README_VERY_LONG_FILE"
        target_len = 10
        res = generate_optimized_filename(filename, target_len, set())
        assert len(res) == 10
        assert res == "README_VER"

        res_collision = generate_optimized_filename(filename, target_len, {"README_VER"})
        assert len(res_collision) == 10
        assert res_collision == "README_V_1"

    def test_small_target_len(self):
        res = generate_optimized_filename("test.tar.gz", 3, set())
        assert len(res) <= 3

    def test_small_target_len_with_collision(self):
        # Target 5 where extension length (8) exceeds target len
        res = generate_optimized_filename("file.longextension", 5, {"file."})
        assert len(res) == 5
        assert res == "fil_1"

        # Target 1 where target < len(num_str)
        res_tiny = generate_optimized_filename("file.txt", 1, {"f"})
        assert len(res_tiny) == 1
        assert res_tiny == "_"


class TestCreateAndPrintLodFiles:
    def test_create_lod_files(self, tmp_path):
        f1 = tmp_path / "hello.txt"
        f1.write_text("content")
        f2 = tmp_path / "sub" / "world.py"
        f2.parent.mkdir()
        f2.write_text("print(1)")

        lod = create_lod_files(str(tmp_path))
        paths = [d["Path"] for d in lod]
        assert str(f1.resolve()) in paths
        assert str(f2.resolve()) in paths

    def test_create_lod_files_none_raises(self):
        with pytest.raises(Exception):
            create_lod_files(None)

    def test_print_lod_files_filtering_and_ordering(self, tmp_path):
        lod = [
            {"Path": "/a/short.txt", "Path length": 12, "Filename length": 9},
            {"Path": "/a/very_very_long.txt", "Path length": 21, "Filename length": 17},
            {"Path": "/b/medium_file.txt", "Path length": 18, "Filename length": 15},
        ]
        # Filter filename >= 15
        filtered = print_lod_files(lod, 0, 15, "FilenameLength")
        assert len(filtered) == 2
        assert filtered[0]["Filename length"] <= filtered[1]["Filename length"]

        # Order by PathLength
        filtered_path = print_lod_files(lod, 15, 0, "PathLength")
        assert len(filtered_path) == 2
        assert filtered_path[0]["Path length"] <= filtered_path[1]["Path length"]

        # Order by Path
        filtered_p = print_lod_files(lod, 0, 0, "Path")
        assert len(filtered_p) == 3
        assert filtered_p[0]["Path"] == "/a/short.txt"


class TestRenameAndUndo:
    def test_rename_by_filename_length_and_undo(self, tmp_path, temp_config_dir):
        long_file = tmp_path / "very_long_file_name_to_be_renamed.txt"
        long_file.write_text("test")
        short_file = tmp_path / "short.txt"
        short_file.write_text("keep")

        lod = create_lod_files(str(tmp_path))
        filtered = print_lod_files(lod, 0, 20, "Path")
        assert len(filtered) == 1

        ops = rename_files(filtered, 0, 20)
        assert len(ops) == 1
        renamed_path = ops[0]["renamed"]
        assert os.path.exists(renamed_path)
        assert not os.path.exists(str(long_file))
        assert len(os.path.basename(renamed_path)) == 20

        # Undo the rename
        undone = undo_rename(1)
        assert undone == 1
        assert os.path.exists(str(long_file))
        assert not os.path.exists(renamed_path)

    def test_rename_collision_avoidance(self, tmp_path, temp_config_dir):
        # Create two files that will truncate to the same name
        f1 = tmp_path / "long_document_alpha.txt"
        f2 = tmp_path / "long_document_bravo.txt"
        f1.write_text("1")
        f2.write_text("2")

        lod = create_lod_files(str(tmp_path))
        filtered = print_lod_files(lod, 0, 15, "Path")
        assert len(filtered) == 2

        ops = rename_files(filtered, 0, 15)
        assert len(ops) == 2
        names = [os.path.basename(op["renamed"]) for op in ops]
        assert len(names) == len(set(names))
        for name in names:
            assert len(name) == 15
            assert os.path.exists(str(tmp_path / name))

        # Undo restores both files
        undone = undo_rename(1)
        assert undone == 2
        assert f1.exists()
        assert f2.exists()

    def test_rename_by_path_length(self, tmp_path, temp_config_dir):
        sub = tmp_path / "deeply" / "nested" / "directory"
        sub.mkdir(parents=True)
        f = sub / "some_rather_long_filename.dat"
        f.write_text("nested")

        orig_path_len = len(str(f))
        target_path_len = orig_path_len - 10

        lod = create_lod_files(str(tmp_path))
        filtered = print_lod_files(lod, target_path_len, 0, "Path")
        ops = rename_files(filtered, target_path_len, 0)
        assert len(ops) == 1
        new_path = ops[0]["renamed"]
        assert len(new_path) == target_path_len
        assert os.path.dirname(new_path) == str(sub)

        # Undo
        undo_rename(1)
        assert f.exists()

    def test_rename_directory_too_long_for_path_limit(self, tmp_path, temp_config_dir, capsys):
        sub = tmp_path / "very" / "long" / "subfolder" / "path"
        sub.mkdir(parents=True)
        f = sub / "file.txt"
        f.write_text("content")

        lod = [{"Path": str(f), "Path length": len(str(f)), "Filename length": len("file.txt")}]
        # Desired path length smaller than directory length
        ops = rename_files(lod, 10, 0)
        assert ops == []
        assert f.exists()
        captured = capsys.readouterr()
        assert "directory path length" in captured.out

    def test_undo_multiple_sessions(self, tmp_path, temp_config_dir):
        f1 = tmp_path / "session1_very_long_file.txt"
        f1.write_text("1")
        lod1 = create_lod_files(str(tmp_path))
        rename_files(lod1, 0, 15)

        f2 = tmp_path / "session2_very_long_file.txt"
        f2.write_text("2")
        lod2 = create_lod_files(str(tmp_path))
        rename_files(lod2, 0, 15)

        # Undo 2 sessions
        undone = undo_rename(2)
        assert undone >= 2
        assert f1.exists()
        assert f2.exists()

    def test_undo_empty_history(self, temp_config_dir, capsys):
        undone = undo_rename(1)
        assert undone == 0
        captured = capsys.readouterr()
        assert "No rename operations to undo" in captured.out

    def test_undo_missing_file(self, tmp_path, temp_config_dir, capsys):
        f = tmp_path / "long_filename_delete_after_rename.txt"
        f.write_text("delete me")
        lod = create_lod_files(str(tmp_path))
        ops = rename_files(lod, 0, 15)
        # Delete the renamed file
        os.remove(ops[0]["renamed"])
        undo_rename(1)
        captured = capsys.readouterr()
        assert "not found" in captured.out

    def test_undo_destination_already_exists(self, tmp_path, temp_config_dir, capsys):
        f = tmp_path / "long_filename_recreated_after_rename.txt"
        f.write_text("orig")
        lod = create_lod_files(str(tmp_path))
        ops = rename_files(lod, 0, 15)
        # Recreate the original file
        f.write_text("new collision")
        undone = undo_rename(1)
        assert undone == 0
        captured = capsys.readouterr()
        assert "already exists" in captured.out

    def test_rename_no_files_need_rename(self, tmp_path, temp_config_dir, capsys):
        f = tmp_path / "short.txt"
        f.write_text("short")
        lod = create_lod_files(str(tmp_path))
        ops = rename_files(lod, 0, 20)
        assert ops == []
        captured = capsys.readouterr()
        assert "No files needed to be renamed" in captured.out

    def test_undo_negative_steps(self, temp_config_dir):
        # steps <= 0 defaults to 1
        res = undo_rename(-5)
        assert res == 0

    def test_corrupt_config_and_history(self, temp_config_dir):
        ensure_user_config()
        config_path = os.path.join(get_user_config_dir(), "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write("{invalid json")
        assert get_config() == {"max_history_entries": 100}

        history_path = os.path.join(get_user_config_dir(), "history.json")
        with open(history_path, "w", encoding="utf-8") as f:
            f.write("{invalid json")
        assert load_history() == []

        with open(history_path, "w", encoding="utf-8") as f:
            json.dump({"not_a": "list"}, f)
        assert load_history() == []

    def test_get_user_config_dir_windows(self, monkeypatch, tmp_path):
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        monkeypatch.setattr("filenamelength.filenamelength.os_name", "nt")
        monkeypatch.setenv("APPDATA", str(tmp_path / "AppData"))
        d = get_user_config_dir()
        assert str(tmp_path / "AppData") in d



class TestMainCLI:
    def test_main_validation_rename_without_limits(self, capsys):
        code = main(["--rename"])
        assert code == 1
        captured = capsys.readouterr()
        assert "requires --minimum_path_length or --minimum_filename_length" in captured.out

    def test_main_validation_rename_and_undo_together(self, capsys):
        code = main(["--minimum_filename_length", "10", "--rename", "--undo"])
        assert code == 1
        captured = capsys.readouterr()
        assert "Cannot use --rename and --undo together" in captured.out

    def test_main_validation_undo_non_positive(self, capsys):
        code = main(["--undo", "0"])
        assert code == 1
        captured = capsys.readouterr()
        assert "--undo value must be greater than 0" in captured.out

    def test_main_full_rename_and_undo_flow(self, tmp_path, temp_config_dir, monkeypatch):
        test_file = tmp_path / "a_very_long_filename_for_main_test.txt"
        test_file.write_text("data")

        monkeypatch.chdir(tmp_path)
        # Run rename
        code = main(["--minimum_filename_length", "15", "--rename"])
        assert code == 0
        assert not test_file.exists()

        # Run undo
        code_undo = main(["--undo"])
        assert code_undo == 0
        assert test_file.exists()


class TestFilesystems:
    def test_fsinfo_lod_contents(self):
        fs = get_fsinfo_lod()
        assert len(fs) > 0
        ext4_entry = next(item for item in fs if item.get("Filesystem") == "ext4")
        assert "255" in ext4_entry["Max filename length"]
