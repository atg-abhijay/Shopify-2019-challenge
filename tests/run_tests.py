import argparse
import os

parser = argparse.ArgumentParser(description="Test manager")
parser.add_argument("--spec", action="store", dest="spec", default="all", help="The following options help you run the appropriate battery of tests or all the tests. Possible options are 'signup', 'signin', 'product', 'all' ")
results = parser.parse_args()

FIRST_TIME_TESTS_RUN = False

if os.path.exists("results.log"):
    FIRST_TIME_TESTS_RUN = True

if not FIRST_TIME_TESTS_RUN:
        os.system("pytest -v -m firsttime | tee -a results.log")

if results.spec == "all":
    os.system('pytest -v -m "not firsttime" | tee -a results.log')
else:
    os.system('pytest -v test_' + results.spec + ".py | tee -a results.log")

