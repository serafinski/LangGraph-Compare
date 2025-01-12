import os
from pathlib import Path
from langgraph_compare import create_experiment, ExperimentPaths


def test_create_experiment(setup_cleanup: Path, capsys):
    """
    Test successful experiment creation with all expected directories and paths.
    """
    # Create experiment
    experiment_name = "test_experiment"
    paths = create_experiment(experiment_name)

    # Capture printed output
    captured = capsys.readouterr()

    # Get the experiments directory from the temporary path
    experiments_dir = setup_cleanup / "experiments"

    # Assert experiment paths object is created correctly
    assert isinstance(paths, ExperimentPaths)
    assert paths.name == experiment_name

    # Assert all directories are created relative to the temporary path
    assert os.path.exists(experiments_dir / experiment_name / "db")
    assert os.path.exists(experiments_dir / experiment_name / "json")
    assert os.path.exists(experiments_dir / experiment_name / "csv")
    assert os.path.exists(experiments_dir / experiment_name / "img")
    assert os.path.exists(experiments_dir / experiment_name / "reports")

    # Assert correct output messages
    assert "Creating new experiment..." in captured.out
    assert f"Successfully created 'experiments/{experiment_name}'" in captured.out
    assert f"Experiment '{experiment_name}' created successfully!" in captured.out


def test_create_experiment_paths_validation(setup_cleanup: Path):
    """
    Test that created paths follow expected structure and naming conventions.
    """
    experiment_name = "path_test"
    paths = create_experiment(experiment_name)

    # Test paths using relative format
    expected_base = os.path.join("experiments", experiment_name)

    # Test database path
    assert paths.database == os.path.join(expected_base, "db", f"{experiment_name}.sqlite")

    # Test directory paths
    assert paths.json_dir == os.path.join(expected_base, "json")
    assert paths.csv_dir == os.path.join(expected_base, "csv")
    assert paths.img_dir == os.path.join(expected_base, "img")
    assert paths.reports_dir == os.path.join(expected_base, "reports")

    # Also verify that the directories actually exist in the temporary path
    temp_base = setup_cleanup / "experiments" / experiment_name
    assert os.path.exists(temp_base / "db")
    assert os.path.exists(temp_base / "json")
    assert os.path.exists(temp_base / "csv")
    assert os.path.exists(temp_base / "img")
    assert os.path.exists(temp_base / "reports")