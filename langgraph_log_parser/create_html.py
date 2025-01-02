import json
from pathlib import Path
import base64
import jinja2
from typing import Any, Dict, List, Optional, Union
import webbrowser
from dataclasses import dataclass


@dataclass
class InfrastructureDirs:
    """Class to hold directory paths for infrastructure data."""
    reports_dir: str
    images_dir: Optional[str] = None

    @classmethod
    def from_default_structure(cls, base_path: str) -> 'InfrastructureDirs':
        """Create paths using default directory structure."""
        return cls(
            reports_dir=str(Path(base_path) / "reports"),
            images_dir=str(Path(base_path) / "img")
        )


class _MetricsFormatter:
    HTML_ARROW = " &rarr; "

    # List of metrics that should be formatted as time
    TIME_METRICS = {
        "avg_case_duration",
        "avg_graph_duration",
        "total_time",
        "processing_time"
    }

    @staticmethod
    def format_time(seconds: float) -> str:
        """Format time in seconds to a readable string."""
        if seconds < 0.1:
            return f"{seconds * 1000:.2f} ms"
        return f"{seconds:.2f} s"

    @staticmethod
    def format_count(value: int) -> str:
        """Format count with a thousand separators."""
        return f"{value:,}"

    @staticmethod
    # Format sequences into a more readable structure - connecting steps with arrows
    def format_sequences(sequences: Dict[str, list]) -> Dict[str, Any]:
        """Format sequences into a more readable structure."""
        return {
            f"Sequence {seq_id}": {
                "steps": len(steps),
                "path": _MetricsFormatter.HTML_ARROW.join(steps)
            }
            for seq_id, steps in sequences.items()
        }

    @staticmethod
    # Same as above but additionally with probabilities
    def format_sequences_with_probabilities(sequences: List) -> Dict[str, Any]:
        """Format sequences with probabilities into a readable structure."""
        return {
            f"Sequence {seq_id}": {
                "steps": len(sequence),
                "probability": f"{probability * 100:.1f}%",
                "path": _MetricsFormatter.HTML_ARROW.join(sequence)
            }
            for seq_id, sequence, probability in sequences
        }

    @staticmethod
    # Format self distances into a more readable structure - how many steps to reach the same activity
    def format_self_distances(distances: Dict[str, Dict[str, int]]) -> Dict[str, Any]:
        """Format self distances into a more readable structure."""
        return {
            f"Sequence {seq_id}": {
                activity: f"{distance} steps"
                for activity, distance in activities.items()
            }
            for seq_id, activities in distances.items()
        }

    @staticmethod
    # Format activities count into a more readable structure - how many times each activity was executed (percentage)
    def format_activities_count(counts: Dict[str, int]) -> Dict[str, str]:
        """Format activity counts with percentage of total."""
        total = sum(counts.values())
        return {
            activity: f"{count:,} ({(count / total) * 100:.1f}%)"
            for activity, count in counts.items()
        }

    @staticmethod
    # Format rework counts into a more readable structure - how many times each activity was reworked (percentage)
    def format_rework_counts(counts: Dict[str, int]) -> Union[str, Dict[str, str]]:
        """Format rework counts with percentages of total activities."""
        if not counts:
            return "No reworks"

        # Get activities count from context
        activities_count = _MetricsFormatter._context.get('activities_count', {})

        result = {}
        for activity, rework_count in counts.items():
            total_activity_count = activities_count.get(activity, 0)
            if total_activity_count > 0:
                percentage = (rework_count / total_activity_count) * 100
                result[activity] = f"{_MetricsFormatter.format_count(rework_count)} ({percentage:.1f}% of activity)"
            else:
                result[activity] = f"{_MetricsFormatter.format_count(rework_count)}"

        return result

    @staticmethod
    def format_metric(key: str, value: Any) -> Any:
        """Format a metric based on its key and value type."""
        # First check if it's a time metric
        if key in _MetricsFormatter.TIME_METRICS and isinstance(value, (int, float)):
            return _MetricsFormatter.format_time(value)

        if isinstance(value, dict):
            formatters = {
                "sequences": _MetricsFormatter.format_sequences,
                "minimum_self_distances": _MetricsFormatter.format_self_distances,
                "activities_count": _MetricsFormatter.format_activities_count,
                "cases_durations": lambda v: {case: _MetricsFormatter.format_time(duration)
                                              for case, duration in v.items()},
                "activities_mean_service_time": lambda v: {activity: _MetricsFormatter.format_time(duration)
                                                           for activity, duration in v.items()},
                "rework_counts": _MetricsFormatter.format_rework_counts
            }
            return formatters.get(key, lambda x: x)(value)
        elif isinstance(value, list) and key == "sequences_with_probabilities":
            return _MetricsFormatter.format_sequences_with_probabilities(value)

        return value

    # Class variable to store the context
    _context = {}

    @classmethod
    def set_context(cls, report_data: Dict):
        """Set the context for formatting metrics."""
        cls._context = report_data


class _ArchitectureComparisonReport:
    DEFAULT_EXPERIMENTS_DIR = "experiments"
    DEFAULT_REPORTS_DIR = "comparison_reports"

    def __init__(
            self,
            infrastructures: Dict[str, Union[str, InfrastructureDirs]],
            base_dir: Optional[str] = None,
            output_dir: Optional[str] = None
    ):
        """
        Initialize the report generator.

        Args:
            infrastructures: Dict mapping infrastructure names to either:
                           - Directory path string (uses default structure)
                           - InfrastructureDirs object (custom directories)
            base_dir: Optional base directory for relative paths
            output_dir: Optional output directory for reports
        """
        self.base_dir = base_dir
        self.infrastructures = infrastructures
        # Allow custom output directory or use default
        self.report_dir = output_dir if output_dir else self.DEFAULT_REPORTS_DIR
        # Ensure the report directory exists
        Path(self.report_dir).mkdir(parents=True, exist_ok=True)

        # Process infrastructure directories
        self.infra_dirs = {}
        for infra_name, dir_info in infrastructures.items():
            if isinstance(dir_info, InfrastructureDirs):
                self.infra_dirs[infra_name] = dir_info
            else:
                # Handle string path
                infra_path = dir_info
                # If it's just a name (no parent directory) and no base_dir was specified,
                # assume it's under the experiments directory
                if not Path(infra_path).parent.name and not self.base_dir:
                    base_path = str(Path(self.DEFAULT_EXPERIMENTS_DIR) / infra_path)
                # If base_dir was specified, use it
                elif self.base_dir:
                    base_path = str(Path(base_dir) / infra_path)
                # Otherwise, use the path as-is
                else:
                    base_path = infra_path
                self.infra_dirs[infra_name] = InfrastructureDirs.from_default_structure(base_path)

        # Storage for data from reports (JSON files)
        self.infrastructures_data = {}
        # Storage for images data (base64 encoded)
        self.images_data = {}
        # Formatter for metrics
        self.formatter = _MetricsFormatter()

    def generate_report_filename(self) -> str:
        """Generate a filename for the report based on compared infrastructures."""
        # Get infrastructure names without path
        infra_names = [Path(infra).name for infra in self.infrastructures]
        # Join with 'vs' and add .html extension
        return f"{'_vs_'.join(infra_names)}.html"

    def load_data(self):
        for infra_name, dirs in self.infra_dirs.items():
            # Storage for data from reports (JSON files)
            self.infrastructures_data[infra_name] = {}
            # Storage for images data (base64 encoded)
            self.images_data[infra_name] = {}

            # Load metrics report data
            metrics_path = Path(dirs.reports_dir) / "metrics_report.json"
            try:
                with open(metrics_path) as f:
                    report_data = json.load(f)
                    # Format the data as needed
                    _MetricsFormatter.set_context(report_data)
                    self.infrastructures_data[infra_name]['main_report'] = {
                        key: self.formatter.format_metric(key, value)
                        for key, value in report_data.items()
                    }
            except FileNotFoundError:
                raise FileNotFoundError(f"Metrics report not found at {metrics_path}")

            # Load sequences report data if available
            sequences_path = Path(dirs.reports_dir) / "sequences_report.json"
            if sequences_path.exists():
                with open(sequences_path) as f:
                    sequences_data = json.load(f)
                    # Format the data as needed
                    # Get and sort sequence probabilities
                    sequence_probabilities = sequences_data.get('sequence_probabilities', [])
                    # Sort by probability in descending order
                    sorted_sequences = sorted(sequence_probabilities, key=lambda x: x[2], reverse=True)

                    formatted_sequences = {
                        'start_activities': sequences_data.get('start_activities', {}),
                        'end_activities': sequences_data.get('end_activities', {}),
                        'sequence_probabilities': sorted_sequences
                    }
                    # Save formatted sequences data
                    self.infrastructures_data[infra_name]['sequences_report'] = formatted_sequences

            # Load images if directory is provided
            if dirs.images_dir and Path(dirs.images_dir).exists():
                for img_file in Path(dirs.images_dir).glob("*.png"):
                    with open(img_file, 'rb') as f:
                        # Encode image as base64 and store in dictionary
                        self.images_data[infra_name][img_file.stem] = base64.b64encode(f.read()).decode('utf-8')

    def generate_report(self, open_browser: bool = True):
        # Generate the report path using the configured directory and automatic filename
        report_filename = self.generate_report_filename()
        report_path = Path(self.report_dir) / report_filename

        # Prepare metrics comparison data
        first_infra = next(iter(self.infrastructures_data))
        # Create a dictionary with metrics as keys and lists of values for each infrastructure
        metrics_comparison = {
            metric: [self.infrastructures_data[infra]['main_report'].get(metric)
                     for infra in self.infrastructures_data]
            for metric in self.infrastructures_data[first_infra]['main_report']
        }

        # Create a dictionary with sequences data for each infrastructure
        sequences_data = {
            infra: data.get('sequences_report', {})
            for infra, data in self.infrastructures_data.items()
        }

        template = self.get_template()
        # Render the template with the data
        html_content = template.render(
            infrastructures_data=self.infrastructures_data,
            images_data=self.images_data,
            metrics_comparison=metrics_comparison,
            sequences_data=sequences_data
        )

        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w') as f:
            f.write(html_content)

        print(f"Report generated at {report_path}")

        if open_browser:
            # Convert to absolute path and file URI format
            file_uri = f"file://{report_path.resolve().as_posix()}"
            webbrowser.open(file_uri)

    @staticmethod
    def get_template():
        """Load the HTML template from file."""
        current_dir = Path(__file__).parent
        template_path = current_dir / "templates" / "comparison_report.html"

        # Create Jinja environment with the template directory
        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path.parent),
            autoescape=True
        )

        return env.get_template("comparison_report.html")


def compare(
        infrastructures: Union[List[str], Dict[str, Union[str, InfrastructureDirs]]],
        base_dir: Optional[str] = None,
        output_dir: Optional[str] = None
) -> None:
    """
    Generate and open HTML comparison report comparing multi-agent infrastructures.

    :param infrastructures: List of infrastructure names or dictionary mapping names to paths. Can be:
                          - List of infrastructure names for default structure
                          - Dict mapping names to directory paths or InfrastructureDirs objects
    :type infrastructures: Union[List[str], Dict[str, Union[str, InfrastructureDirs]]]
    :param base_dir: Base directory where all experiments are stored, defaults to "experiments"
    :type base_dir: Optional[str]
    :param output_dir: Directory where generated reports will be saved, defaults to "comparison_reports"
    :type output_dir: Optional[str]

    **Examples:**

    Basic usage with default directory structure::

        compare(["test_1", "test_2"])

    Using custom paths with default subdirectory structure::

        # Will use path/to/test1/reports/ and path/to/test1/img/
        compare({
            "test_1": "path/to/test1",
            "test_2": "path/to/test2"
        })

    Using fully custom directory paths::

        compare({
            "test_1": InfrastructureDirs(
                reports_dir="custom/path1/my_reports",
                images_dir="custom/path1/my_images"
            ),
            "test_2": InfrastructureDirs(
                reports_dir="custom/path2/my_reports"
            )
        })

    Save to specific output directory::

        compare(infrastructures, output_dir="my_reports")
    """
    # Convert list to dict if necessary
    if isinstance(infrastructures, list):
        infrastructures = {infra: infra for infra in infrastructures}

    report_generator = _ArchitectureComparisonReport(infrastructures, base_dir, output_dir)
    report_generator.load_data()
    report_generator.generate_report()