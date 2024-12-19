import os
import sys
import subprocess
import venv
import argparse

class PythonDevMCP:
    def __init__(self, project_path):
        self.project_path = project_path
        self.venv_path = os.path.join(project_path, 'venv')
    
    def create_virtual_environment(self):
        """Create a new virtual environment"""
        try:
            venv.create(self.venv_path, with_pip=True)
            print(f"✅ Virtual environment created at {self.venv_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating virtual environment: {e}")
            return False
    
    def install_dependencies(self, requirements_file=None):
        """Install project dependencies"""
        if not requirements_file:
            requirements_file = os.path.join(self.project_path, 'requirements.txt')
        
        pip_path = os.path.join(self.venv_path, 'bin', 'pip')
        
        try:
            subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
            
            if os.path.exists(requirements_file):
                subprocess.run([pip_path, 'install', '-r', requirements_file], check=True)
                print(f"✅ Dependencies installed from {requirements_file}")
            else:
                print("⚠️ No requirements.txt found. Skipping dependency installation.")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Dependency installation error: {e}")
            return False
    
    def run_tests(self, test_dir='tests'):
        """Run project tests"""
        pytest_path = os.path.join(self.venv_path, 'bin', 'pytest')
        test_path = os.path.join(self.project_path, test_dir)
        
        try:
            if not os.path.exists(pytest_path):
                subprocess.run([os.path.join(self.venv_path, 'bin', 'pip'), 'install', 'pytest'], check=True)
            
            subprocess.run([pytest_path, test_path], check=True)
            print("✅ All tests passed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Some tests failed.")
            return False
    
    def lint_code(self, lint_dirs=['.']):
        """Lint Python code"""
        try:
            pylint_path = os.path.join(self.venv_path, 'bin', 'pylint')
            
            if not os.path.exists(pylint_path):
                subprocess.run([os.path.join(self.venv_path, 'bin', 'pip'), 'install', 'pylint'], check=True)
            
            for directory in lint_dirs:
                full_dir = os.path.join(self.project_path, directory)
                subprocess.run([pylint_path, full_dir], check=True)
            
            print("✅ Code linting completed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Code linting found issues.")
            return False
    
    def generate_documentation(self, output_dir='docs'):
        """Generate documentation using Sphinx"""
        try:
            sphinx_path = os.path.join(self.venv_path, 'bin', 'sphinx-build')
            
            if not os.path.exists(sphinx_path):
                subprocess.run([os.path.join(self.venv_path, 'bin', 'pip'), 'install', 'sphinx'], check=True)
            
            docs_source = os.path.join(self.project_path, 'docs_source')
            docs_output = os.path.join(self.project_path, output_dir)
            
            subprocess.run([sphinx_path, '-b', 'html', docs_source, docs_output], check=True)
            print(f"✅ Documentation generated at {docs_output}")
            return True
        except subprocess.CalledProcessError:
            print("❌ Documentation generation failed.")
            return False

def main():
    parser = argparse.ArgumentParser(description="Python Development MCP")
    parser.add_argument('--action', choices=['create_env', 'install_deps', 'test', 'lint', 'docs'], 
                        help="Development action to perform")
    args = parser.parse_args()
    
    project_path = os.path.dirname(os.path.abspath(__file__))
    dev_mcp = PythonDevMCP(project_path)
    
    actions = {
        'create_env': dev_mcp.create_virtual_environment,
        'install_deps': dev_mcp.install_dependencies,
        'test': dev_mcp.run_tests,
        'lint': dev_mcp.lint_code,
        'docs': dev_mcp.generate_documentation
    }
    
    if args.action:
        actions[args.action]()
    else:
        print("No action specified. Use --help for available actions.")

if __name__ == '__main__':
    main()
