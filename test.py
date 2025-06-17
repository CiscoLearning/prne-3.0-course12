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

        test_id_to_fetch = None

        for test_id, test_info in tests.items():
            if test_info['testName'] == test_name:
                test_id_to_fetch = test_id
                print(f"\nFound test '{test_name}' with ID: {test_id_to_fetch}")
                break

        if test_id_to_fetch is None:
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
            test_id_to_fetch = created_test.get('testId')
            print(f"Test created successfully with ID: {test_id_to_fetch}")
            print(f"Test URL: {created_test.get('apiLinks', {}).get('test', {}).get('href')}")

        if test_id_to_fetch:
            print(f"\nFetching latest result for test ID {test_id_to_fetch}:")
            test_info = tests.get(test_id_to_fetch)
            links = test_info.get("testResultsLinks") if test_info else None

            if links:
                results_link = links[0]["href"]
                print(f"Using results link: {results_link}")
                test_result: TE.models.TestResult = api.get_test_results_by_link(results_link)

                for field in ("test_id", "test_name", "status", "timestamp"):
                    label = field.replace("_", " ").title()
                    print(f"{label}: {getattr(test_result, field, None)}")

                print("Metrics:")
                metrics = getattr(test_result, "metrics", None)
                if metrics:
                    for name, value in metrics.items():
                        print(f"  {name}: {value}")
                else:
                    print("  No metrics available.")
            else:
                print(f"Could not find test {test_id_to_fetch} or no results link available.")
        else:
            print(f"\nCould not find or create test '{test_name}'. Cannot fetch results.")

    except ValueError as e:
        print(f"Authentication Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
