### This works for unittests only ###

1. Add test_discovery_execution.py and input.yaml in the repo.
2. Add the starting directory and the pattern in the input.yaml as:
    - start_dir: <directory having tests> 
    (eg tests/)
    - pattern: '<test file pattern>' 
    (eg: 'test_*.py')
3. Run python3 test_discovery_execution.py