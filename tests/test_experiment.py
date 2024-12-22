import os
from langgraph_log_parser import create_experiment, ExperimentPaths

def test_create_experiment(setup_cleanup, capsys):
    """
    Test successful experiment creation with all expected directories and paths.
    """
    # Create experiment
    experiment_name = "test_experiment"
    paths = create_experiment(experiment_name)

    # Capture printed output
    captured = capsys.readouterr()

    # Assert experiment paths object is created correctly
    assert isinstance(paths, ExperimentPaths)
    assert paths.name == experiment_name

    # Assert all directories are created
    assert os.path.exists(paths.database.replace(f"{experiment_name}.sqlite", ""))
    assert os.path.exists(paths.json_dir)
    assert os.path.exists(paths.csv_dir)
    assert os.path.exists(paths.img_dir)
    assert os.path.exists(paths.reports_dir)

    # Assert correct output messages
    assert "Creating new experiment..." in captured.out
    assert f"Successfully created 'experiments/{experiment_name}'" in captured.out
    assert f"Experiment '{experiment_name}' created successfully!" in captured.out


def test_create_experiment_paths_validation(setup_cleanup):
    """
    Test that created paths follow expected structure and naming conventions.
    """
    experiment_name = "path_test"
    paths = create_experiment(experiment_name)

    # Test database path
    assert paths.database == os.path.join("experiments", experiment_name, "db", f"{experiment_name}.sqlite")

    # Test directory paths
    assert paths.json_dir == os.path.join("experiments", experiment_name, "json")
    assert paths.csv_dir == os.path.join("experiments", experiment_name, "csv")
    assert paths.img_dir == os.path.join("experiments", experiment_name, "img")
    assert paths.reports_dir == os.path.join("experiments", experiment_name, "reports")