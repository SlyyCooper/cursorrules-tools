import anthropic
from pathlib import Path
import json
from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
from rich.panel import Panel
from typing import Dict, List, Optional, Union

class ClaudeAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic()
        self.console = Console()

    def find_dependency_files(self, path: Union[str, Path]) -> Dict[str, Path]:
        """
        Find package.json and/or requirements.txt in the given path.
        
        Args:
            path: Directory path to search in
            
        Returns:
            Dictionary of found dependency files
        """
        path = Path(path)
        dependency_files = {}
        
        # Check for package.json
        package_json = path / 'package.json'
        if package_json.exists():
            dependency_files['package.json'] = package_json
            
        # Check for requirements.txt
        requirements_txt = path / 'requirements.txt'
        if requirements_txt.exists():
            dependency_files['requirements.txt'] = requirements_txt
            
        return dependency_files

    def analyze_project_dependencies(self, path: Union[str, Path]) -> Dict[str, dict]:
        """
        Analyze all dependency files found in the given path.
        
        Args:
            path: Directory path containing dependency files
            
        Returns:
            Dictionary containing analysis results for each dependency file
        """
        path = Path(path)
        if not path.exists():
            self.console.print(f"[bold red]Error: Path {path} does not exist[/bold red]")
            return {}
            
        dependency_files = self.find_dependency_files(path)
        if not dependency_files:
            self.console.print(f"[bold yellow]No dependency files (package.json/requirements.txt) found in {path}[/bold yellow]")
            return {}
            
        analysis_results = {}
        
        for file_name, file_path in dependency_files.items():
            self.console.print(f"\n[bold blue]Found {file_name}, analyzing...[/bold blue]")
            analysis = self.analyze_dependencies(str(file_path))
            if analysis:
                analysis_results[file_name] = analysis
                # Format and display the results
                markdown = self.format_analysis_markdown(analysis, Path(file_name).suffix)
                self.console.print(Markdown(markdown))
            
        return analysis_results

    def analyze_dependencies(self, file_path: str) -> dict:
        """Analyze package.json or requirements.txt with Claude-3-5-sonnet-20241022 and return the analysis."""
        try:
            # Read the file
            with open(file_path, 'r') as f:
                file_content = f.read()

            file_type = Path(file_path).suffix
            if file_type == '.json':
                system = """You are a dependency version analyzer. Output ONLY in this exact JSON format:
{
    "package_versions": [
        {
            "name": "package-name",
            "current_version": "version-specified",
            "latest_version": "latest-available",
            "is_latest": boolean,
            "version_gap": "semantic version difference"
        }
    ],
    "metadata": {
        "total_packages": number,
        "outdated_count": number,
        "analysis_date": "YYYY-MM-DD"
    }
}"""
                prompt = f"Extract and analyze version information from this package.json:\n\n{file_content}"
            else:  # requirements.txt
                system = """You are a Python dependency version analyzer. Output ONLY in this exact JSON format:
{
    "python_versions": [
        {
            "name": "package-name",
            "specified_version": "version-constraint",
            "latest_version": "latest-available",
            "is_compatible": boolean,
            "min_python_version": "minimum-python-version"
        }
    ],
    "metadata": {
        "total_packages": number,
        "packages_with_constraints": number,
        "analysis_date": "YYYY-MM-DD"
    }
}"""
                prompt = f"Extract and analyze version information from this requirements.txt:\n\n{file_content}"

            self.console.print(f"\n[bold blue]Starting analysis with Claude-3-5-sonnet-20241022 for {Path(file_path).name}...[/bold blue]")
            
            # Initialize response accumulator
            full_response = ""
            current_content = ""
            
            # Create a live display for the streaming output
            with Live(Panel("Analyzing...", title="Claude-3-5-sonnet-20241022 Analysis", border_style="blue"), refresh_per_second=4) as live:
                with self.client.messages.stream(
                    max_tokens=1024,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }],
                    model="claude-3-7-sonnet-20250219",
                    system=system,
                    temperature=0.0
                ) as stream:
                    for event in stream:
                        if event.type == "message_start":
                            live.update(Panel("Starting analysis...", title="Claude-3-5-sonnet-20241022 Analysis", border_style="blue"))
                        elif event.type == "content_block_start":
                            current_content = ""
                        elif event.type == "content_block_delta":
                            if event.delta.type == "text_delta":
                                text = event.delta.text
                                current_content += text
                                full_response += text
                                # Update the live display with the current content
                                live.update(Panel(current_content, title="Claude-3-5-sonnet-20241022 Analysis", border_style="blue"))
                        elif event.type == "content_block_stop":
                            # Content block is complete
                            pass
                        elif event.type == "message_delta":
                            if event.delta.stop_reason:
                                live.update(Panel("Analysis complete!", title="Claude-3-5-sonnet-20241022 Analysis", border_style="green"))
                        elif event.type == "message_stop":
                            # Message is complete
                            pass
                        elif event.type == "error":
                            error_msg = f"Error: {event.error.message}"
                            live.update(Panel(error_msg, title="Error", border_style="red"))
                            raise Exception(error_msg)

            try:
                # Parse the JSON response
                analysis = json.loads(full_response)
                return analysis
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw response in a structured format
                return {
                    "raw_analysis": full_response,
                    "error": "Could not parse response as JSON"
                }

        except FileNotFoundError:
            self.console.print(f"[bold red]Error: {Path(file_path).name} not found[/bold red]")
            return None
        except Exception as e:
            self.console.print(f"[bold red]Error during analysis: {str(e)}[/bold red]")
            return None

    def format_analysis_markdown(self, analysis: dict, file_type: str) -> str:
        """Convert the analysis to a nicely formatted markdown string."""
        if not analysis:
            return "\n\n## Dependency Analysis\nError during analysis."
            
        if "raw_analysis" in analysis:
            return f"\n\n## Dependency Analysis\n\n{analysis['raw_analysis']}"

        md = "\n\n## Dependency Version Analysis\n\n"
        
        if file_type == '.json':  # package.json format
            md += f"Analysis Date: {analysis['metadata']['analysis_date']}\n\n"
            md += f"Total Packages: {analysis['metadata']['total_packages']}\n"
            md += f"Outdated Packages: {analysis['metadata']['outdated_count']}\n\n"
            
            md += "### Package Versions\n"
            for pkg in analysis['package_versions']:
                status = "✅" if pkg['is_latest'] else "⚠️"
                md += f"{status} **{pkg['name']}**\n"
                md += f"  - Current: `{pkg['current_version']}`\n"
                md += f"  - Latest: `{pkg['latest_version']}`\n"
                if not pkg['is_latest']:
                    md += f"  - Version Gap: {pkg['version_gap']}\n"
                md += "\n"
            
        else:  # requirements.txt format
            md += f"Analysis Date: {analysis['metadata']['analysis_date']}\n\n"
            md += f"Total Packages: {analysis['metadata']['total_packages']}\n"
            md += f"Packages with Version Constraints: {analysis['metadata']['packages_with_constraints']}\n\n"
            
            md += "### Python Package Versions\n"
            for pkg in analysis['python_versions']:
                status = "✅" if pkg['is_compatible'] else "⚠️"
                md += f"{status} **{pkg['name']}**\n"
                md += f"  - Specified: `{pkg['specified_version']}`\n"
                md += f"  - Latest: `{pkg['latest_version']}`\n"
                md += f"  - Min Python: `{pkg['min_python_version']}`\n\n"
        
        return md

    def analyze_directory_structure(self, tree_content: str) -> dict:
        """Analyze directory structure and provide file descriptions."""
        system = """You are a code structure analyzer. For each file in the directory tree, provide a brief (max 50 chars) 
        description of its purpose based on its name and location. Output in this exact JSON format:
        {
            "file_descriptions": {
                "path/to/file.ext": "Brief description of file purpose",
                "another/path/file.ext": "Another brief description"
            }
        }
        Exclude directories and focus only on files."""
        
        prompt = f"Analyze this directory tree and provide brief descriptions for each file:\n\n{tree_content}"
        
        self.console.print("\n[bold blue]Analyzing directory structure with Claude-3-5-sonnet-20241022...[/bold blue]")
        
        full_response = ""
        current_content = ""
        
        with Live(Panel("Analyzing directory structure...", title="Claude-3-5-sonnet-20241022 Analysis", border_style="blue"), refresh_per_second=4) as live:
            with self.client.messages.stream(
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                model="claude-3-7-sonnet-20250219",
                system=system,
                temperature=0.0
            ) as stream:
                for event in stream:
                    if event.type == "message_start":
                        live.update(Panel("Starting analysis...", title="Claude-3-5-sonnet-20241022 Analysis", border_style="blue"))
                    elif event.type == "content_block_start":
                        current_content = ""
                    elif event.type == "content_block_delta":
                        if event.delta.type == "text_delta":
                            text = event.delta.text
                            current_content += text
                            full_response += text
                            # Update the live display with the current content
                            live.update(Panel(current_content, title="Claude-3-5-sonnet-20241022 Analysis", border_style="blue"))
                    elif event.type == "content_block_stop":
                        # Content block is complete
                        pass
                    elif event.type == "message_delta":
                        if event.delta.stop_reason:
                            live.update(Panel("Analysis complete!", title="Claude-3-5-sonnet-20241022 Analysis", border_style="green"))
                    elif event.type == "message_stop":
                        # Message is complete
                        pass
                    elif event.type == "error":
                        error_msg = f"Error: {event.error.message}"
                        live.update(Panel(error_msg, title="Error", border_style="red"))
                        raise Exception(error_msg)

        try:
            return json.loads(full_response)
        except json.JSONDecodeError:
            return {"file_descriptions": {}}

if __name__ == "__main__":
    analyzer = ClaudeAnalyzer()
    # Example usage with path
    analyzer.analyze_project_dependencies(".")
    