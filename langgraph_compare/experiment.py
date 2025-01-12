import os
import sqlite3
from dataclasses import dataclass
from typing import Optional
from langgraph.checkpoint.sqlite import SqliteSaver

@dataclass
class ExperimentPaths:
    """
    Class that holds and manages all paths for an experiment.

    :param name: Name of the experiment that will be used for folder structure.
    :type name: str
    :param base_dir: Base directory where all experiments are stored, defaults to "experiments".
    :type base_dir: str
    """
    name: str
    base_dir: str = "experiments"
    _connection: Optional[sqlite3.Connection] = None
    _memory: Optional[SqliteSaver] = None

    @property
    def database(self) -> str:
        """
        Returns path to the main SQLite database.

        :return: Full path to the SQLite database file.
        :rtype: str

        **Example:**

        >>> paths = ExperimentPaths("test")
        >>> paths.database
        'experiments/test/db/test.sqlite'
        """
        return os.path.join(self.base_dir, self.name, "db", f"{self.name}.sqlite")

    @property
    def connection(self) -> sqlite3.Connection:
        """
        Returns or creates SQLite connection with appropriate settings.

        :return: SQLite connection object
        :rtype: sqlite3.Connection

        **Example:**

        >>> paths = ExperimentPaths("test")
        >>> conn = paths.connection  # Creates new connection if none exists
        >>> conn2 = paths.connection  # Returns existing connection
        """
        if self._connection is None:
            self._connection = sqlite3.connect(self.database, check_same_thread=False)
        return self._connection

    @property
    def memory(self) -> SqliteSaver:
        """
        Returns or creates SqliteSaver instance for the database.

        :return: SqliteSaver instance
        :rtype: SqliteSaver

        **Example:**

        >>> paths = ExperimentPaths("test")
        >>> saver = paths.memory  # Creates new SqliteSaver if none exists
        >>> saver2 = paths.memory  # Returns existing SqliteSaver
        """
        if self._memory is None:
            self._memory = SqliteSaver(self.connection)
        return self._memory

    @property
    def json_dir(self) -> str:
        """
        Returns path to the json directory.

        :return: Full path to the JSON directory.
        :rtype: str

        **Example:**

        >>> paths = ExperimentPaths("test")
        >>> paths.json_dir
        'experiments/test/json'
        """
        return os.path.join(self.base_dir, self.name, "json")

    @property
    def csv_dir(self) -> str:
        """
        Returns path to the csv directory.

        :return: Full path to the CSV directory.
        :rtype: str

        **Example:**

        >>> paths = ExperimentPaths("test")
        >>> paths.csv_dir
        'experiments/test/csv'
        """
        return os.path.join(self.base_dir, self.name, "csv")

    @property
    def img_dir(self) -> str:
        """
        Returns path to the img directory.

        :return: Full path to the images directory.
        :rtype: str

        **Example:**

        >>> paths = ExperimentPaths("test")
        >>> paths.img_dir
        'experiments/test/img'
        """
        return os.path.join(self.base_dir, self.name, "img")

    @property
    def reports_dir(self) -> str:
        """
        Returns path to the reports directory.

        :return: Full path to the reports directory.
        :rtype: str

        **Example:**

        >>> paths = ExperimentPaths("test")
        >>> paths.reports_dir
        'experiments/test/reports'
        """
        return os.path.join(self.base_dir, self.name, "reports")

    def get_csv_path(self, filename: str = "csv_output.csv") -> str:
        """
        Returns full path for a CSV file.

        :param filename: Name of the CSV file.
        :type filename: str
        :return: Full path to the CSV file.
        :rtype: str

        **Example:**

        >>> paths = ExperimentPaths("test")
        >>> paths.get_csv_path("data.csv")
        'experiments/test/csv/data.csv'
        """
        return os.path.join(self.csv_dir, filename)

    def get_img_path(self, filename: Optional[str] = None) -> str:
        """
        Returns full path for an image file.

        :param filename: Name of the image file, if None uses the default from the calling function
        :type filename: Optional[str]
        :return: Full path to the image file.
        :rtype: str

        **Example:**

        >>> paths = ExperimentPaths("test")
        >>> paths.get_img_path("plot.png")
        'experiments/test/img/plot.png'
        >>> # When used in functions, will use that function's default
        >>> generate_prefix_tree(event_log, paths.get_img_path())  # Will use 'tree.png'
        >>> generate_dfg(event_log, paths.get_img_path())  # Will use 'dfg.png'
        """
        if filename is None:
            return self.img_dir
        return os.path.join(self.img_dir, filename)


def _create_folder_structure(folder_name: str, base_dir: str = "experiments") -> None:
    """
    Create a folder structure with db, img, json, csv, and reports subfolders.

    :param folder_name: Name of the main folder to be created inside base directory.
    :type folder_name: str
    :param base_dir: Base directory where the experiment folder will be created, defaults to "experiments".
    :type base_dir: str

    **Example:**

    >>> _create_folder_structure("test_directory", base_dir="custom_experiments")
    Successfully created 'custom_experiments/test_directory' with subfolders: db, img, json, csv, reports
    """
    # Create base directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Full path for the main folder
    full_path = os.path.join(base_dir, folder_name)

    # Check if folder exists
    if os.path.exists(full_path):
        raise FileExistsError(f"Error: Folder '{full_path}' already exists!")

    try:
        # Create main folder inside base directory
        os.makedirs(full_path)

        # Create all subfolders
        basic_subfolders = ['db', 'img', 'json', 'csv', 'reports']
        for subfolder in basic_subfolders:
            subfolder_path = os.path.join(full_path, subfolder)
            os.makedirs(subfolder_path)

        print(f"Successfully created '{full_path}' with subfolders: {', '.join(basic_subfolders)}")

    except OSError as error:
        print(f"Error creating folder structure: {error}")


def create_experiment(name: str, base_dir: str = "experiments") -> ExperimentPaths:
    """
    Main function to set up experiment and return paths. This is the main entry point
    for creating a new experiment structure.

    :param name: Name of the experiment to be created.
    :type name: str
    :param base_dir: Base directory where the experiment folder will be created, defaults to "experiments".
    :type base_dir: str
    :return: ExperimentPaths object containing all relevant paths.
    :rtype: ExperimentPaths

    **Example:**

    >>> paths = create_experiment("my_experiment", base_dir="custom_experiments")
    Creating new experiment...
    Successfully created 'custom_experiments/my_experiment' with subfolders: db, img, json, csv, reports
    Experiment 'my_experiment' created successfully!
    Database path: custom_experiments/my_experiment/db/my_experiment.sqlite
    JSON directory: custom_experiments/my_experiment/json
    CSV directory: custom_experiments/my_experiment/csv
    Image directory: custom_experiments/my_experiment/img
    Reports directory: custom_experiments/my_experiment/reports
    """
    print("\nCreating new experiment...")
    _create_folder_structure(name, base_dir)
    paths = ExperimentPaths(name, base_dir)

    print(f"\nExperiment '{paths.name}' created successfully!")
    print(f"Database path: {paths.database}")
    print(f"JSON directory: {paths.json_dir}")
    print(f"CSV directory: {paths.csv_dir}")
    print(f"Image directory: {paths.img_dir}")
    print(f"Reports directory: {paths.reports_dir}")
    return paths