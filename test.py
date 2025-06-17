import os

from dotenv import load_dotenv

import te_wrapper as TE

def main():
    load_dotenv()

    try:
        te = TE.ThousandEyes()
        print("ThousandEyesAuth initialized successfully.")

        api = te.api
        print("ThousandEyesAPI initialized successfully.")

        print("\nListing all ThousandEyes tests:")
        tests = api.list_tests()
        print(f"Found {len(tests)} tests.")
        for test_id, test_info in tests.items():
            print(f"  ID: {test_id}, Name: {test_info['testName']}")

        test_name = os.getenv('TEST_NAME', 'API Example Test')
        target_url = os.getenv('TARGET', 'https://www.thousandeyes.com')

        if not api.test_exists(name=test_name):
            print(f"\nTest '{test_name}' does not exist. Creating it...")

            print("\nFetching the first agent ID:")
            agent_id = api.get_first_agent_id()
            print(f"First agent ID: {agent_id}")

            test_config = {
                "testName": test_name,
                "testType": "http-server",
                "url": target_url,
                "agents": [{"agentId": agent_id}],
                "interval": 3600,
            }

            print("\nCreating a new HTTP server test:")
            created_test = api.create_test(test_config)
            print(f"Test created successfully with ID: {created_test.get('testId')}")
        else:
            print(f"\nTest '{test_name}' already exists. Skipping creation.")

    except ValueError as e:
        print(f"Authentication Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
