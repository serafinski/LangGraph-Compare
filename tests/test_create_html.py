from langgraph_compare.create_html import compare

def test_generated_report_matches_reference(test_infrastructure, reference_html, setup_cleanup):
    """Test that generated report matches the reference file."""
    # Generate report in test environment
    output_dir = setup_cleanup / "output"
    output_dir.mkdir(exist_ok=True)

    # Run the compare function with our test infrastructure
    compare({"tests/files": str(test_infrastructure)}, output_dir=str(output_dir))

    # Read generated report
    generated_report_path = next(output_dir.glob("*.html"))
    with open(generated_report_path, 'r') as f:
        generated_content = f.read()

    # Compare contents
    def normalize_html(content):
        """Normalize HTML content to ignore irrelevant differences."""
        import re
        # Remove whitespace between tags
        content = re.sub(r'>\s+<', '><', content)
        # Remove all whitespace variations
        content = re.sub(r'\s+', ' ', content)
        # Remove any absolute paths
        content = re.sub(r'file://[^"\']+', '', content)
        return content.strip()

    assert normalize_html(generated_content) == normalize_html(reference_html)