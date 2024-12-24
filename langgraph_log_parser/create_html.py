import json
from pathlib import Path
import base64
import jinja2
from typing import Any, Dict, List, Optional, Union
import webbrowser


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
    def format_activities_count(counts: Dict[str, int]) -> Dict[str, str]:
        """Format activity counts with percentage of total."""
        total = sum(counts.values())
        return {
            activity: f"{count:,} ({(count / total) * 100:.1f}%)"
            for activity, count in counts.items()
        }

    @staticmethod
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
    DEFAULT_REPORTS_DIR = Path("comparison_reports")

    def __init__(self, infrastructures, base_dir=None, output_dir=None):
        self.base_dir = Path(base_dir) if base_dir else None
        self.base_paths = []
        self.infrastructures = infrastructures
        # Allow custom output directory or use default
        self.report_dir = Path(output_dir) if output_dir else self.DEFAULT_REPORTS_DIR
        # Ensure the report directory exists
        self.report_dir.mkdir(parents=True, exist_ok=True)

        for infra in infrastructures:
            infra_path = Path(infra)

            # If it's just a name (no parent directory) and no base_dir was specified,
            # assume it's under the experiments directory
            if not infra_path.parent.name and not self.base_dir:
                self.base_paths.append(Path(self.DEFAULT_EXPERIMENTS_DIR) / infra_path)
            # If base_dir was specified, use it
            elif self.base_dir:
                self.base_paths.append(self.base_dir / infra_path)
            # Otherwise, use the path as-is
            else:
                self.base_paths.append(infra_path)

        self.infrastructures_data = {}
        self.images_data = {}
        self.formatter = _MetricsFormatter()

    def generate_report_filename(self) -> str:
        """Generate a filename for the report based on compared infrastructures."""
        # Get infrastructure names without path
        infra_names = [Path(infra).name for infra in self.infrastructures]
        # Join with 'vs' and add .html extension
        return f"{'_vs_'.join(infra_names)}.html"

    def load_data(self):
        for base_path in self.base_paths:
            infra_name = base_path.name
            self.infrastructures_data[infra_name] = {}
            self.images_data[infra_name] = {}

            # Load metrics report data
            metrics_report_path = base_path / "reports" / "metrics_report.json"
            with open(metrics_report_path) as f:
                report_data = json.load(f)
                _MetricsFormatter.set_context(report_data)
                self.infrastructures_data[infra_name]['main_report'] = {
                    key: self.formatter.format_metric(key, value)
                    for key, value in report_data.items()
                }

            # Load sequences report data
            sequences_report_path = base_path / "reports" / "sequences_report.json"
            if sequences_report_path.exists():
                with open(sequences_report_path) as f:
                    sequences_data = json.load(f)
                    # Format the data as needed
                    # Get and sort sequence probabilities
                    sequence_probabilities = sequences_data.get('sequence_probabilities', [])
                    sorted_sequences = sorted(sequence_probabilities, key=lambda x: x[2], reverse=True)

                    formatted_sequences = {
                        'start_activities': sequences_data.get('start_activities', {}),
                        'end_activities': sequences_data.get('end_activities', {}),
                        'sequence_probabilities': sorted_sequences
                    }
                    self.infrastructures_data[infra_name]['sequences_report'] = formatted_sequences

            # Load images
            img_path = base_path / "img"
            for img_file in img_path.glob("*.png"):
                with open(img_file, 'rb') as f:
                    self.images_data[infra_name][img_file.stem] = base64.b64encode(f.read()).decode('utf-8')

    def generate_report(self, open_browser: bool = True):
        # Generate the report path using the configured directory and automatic filename
        report_filename = self.generate_report_filename()
        report_path = self.report_dir / report_filename

        # Prepare metrics comparison data
        first_infra = next(iter(self.infrastructures_data))
        metrics_comparison = {
            metric: [self.infrastructures_data[infra]['main_report'].get(metric)
                     for infra in self.infrastructures_data]
            for metric in self.infrastructures_data[first_infra]['main_report']
        }

        # Prepare sequences data
        sequences_data = {
            infra: data.get('sequences_report', {})
            for infra, data in self.infrastructures_data.items()
        }

        template = self.get_template()
        html_content = template.render(
            infrastructures_data=self.infrastructures_data,
            images_data=self.images_data,
            metrics_comparison=metrics_comparison,
            sequences_data=sequences_data
        )

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


def compare(infrastructures: list, output_dir: Optional[str] = None) -> None:
    """
    Generate and open HTML comparison report comparing multi-agent infrastructures.
    The report filename is automatically generated based on the compared architectures.

    :param infrastructures: List of infrastructures to compare.
    :type infrastructures: list
    :param output_dir: Optional directory where reports should be saved. If not provided, reports will be saved in the default 'comparison_reports' directory.
    :type output_dir: str, optional

    **Example:**

    .. code-block:: python

        # List the experiments you would like to compare
        infrastructures = ["test_1", "test_2"]

        # Basic usage (saves to default location)
        compare(infrastructures)
        # Output: Report generated at comparison_reports/test_1_vs_test_2.html

        # Save to specific directory
        compare(infrastructures, output_dir="my_reports")
        # Output: Report generated at my_reports/test_1_vs_test_2.html
    """
    report_generator = _ArchitectureComparisonReport(infrastructures, output_dir=output_dir)
    report_generator.load_data()
    report_generator.generate_report()