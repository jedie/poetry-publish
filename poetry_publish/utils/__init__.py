try:
    from creole.setup_utils import update_rst_readme
except ModuleNotFoundError:
    def update_rst_readme():
        # no-op, just print a warning
        print("WARNING: python-creole package is not installed.")
