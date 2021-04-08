from os import system
from pip._internal.utils.misc import get_installed_distributions
from runas import runas


def check_dependencies():
    """Install all the dependencies listed within requirements.txt"""
    with open('requirements.txt', 'r') as dependencies:
        dependencies = set(dependencies.read().split())
    # set of requirements.txt
    dependencies = {i for i in dependencies}
    installed_pkgs = get_installed_distributions()
    # set of all installed pip packages
    installed_pkgs = {str(i).split()[0].lower() for i in installed_pkgs}
    # set of dependencies that must be installed
    dependencies = dependencies.difference(installed_pkgs)
    if dependencies:
        print(f'Found {len(dependencies)} packages to install')
        for dep in dependencies:
            system(f'pip install {dep}')
            print(f'{dep.ljust(30, " ")} OK!')
        return 'OK'
    else:
        print(f'All the dependencies satisfied')
        return 'OK'


if __name__ == '__main__':
    check_dependencies()
    from gateway import main
    runas(main)
