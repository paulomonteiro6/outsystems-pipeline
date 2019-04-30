# Python Modules
import xunitparser, json, os, requests, sys, argparse

# Workaround for Jenkins:
# Set the path to include the outsystems module
# Jenkins exposes the workspace directory through env.
if "WORKSPACE" in os.environ:
    sys.path.append(os.environ['WORKSPACE'])
else:  # Else just add the project dir
    sys.path.append(os.getcwd())

# Custom Modules
from outsystems.vars.file_vars import ARTIFACT_FOLDER, JUNIT_TEST_RESULTS_FILE
from custom_pipeline.slack.send_slack_message import send_slack_message

############################################################## SCRIPT ##############################################################
def main(artifact_dir: str, slack_hook: str, slack_channels: list, pipeline_type: str, job_name: str, job_url: str):
    filename = os.path.join(artifact_dir, JUNIT_TEST_RESULTS_FILE)
    _, tr = xunitparser.parse(open(filename))

    message = "*{}* BDD tests run.\n*{}* errors found.".format(
        tr.testsRun, len(tr.failures))
    # Add test report url
    message += "\n\nGo here for full test report: {}\n\n".format(job_url)

    if len(tr.failures) > 0:
        message += "\nIt failed on the following tests:\n"
        for failure in tr.failures:
            failure_msg = failure[1]
            
            # Get the test name
            test_name = failure_msg.split("Test Name:")[1]
            test_name = test_name.split(";")[0]
            # Get the test module
            test_module = failure_msg.split("Test Module:")[1]
            test_module = test_module.split(" ")[0]
            
            message += "*{} ({})*\n".format(test_name, test_module)

    job_status = (len(tr.failures) <= 0)
    send_slack_message(slack_hook, slack_channels, pipeline_type, "*Test Results for {}:*".format(job_name), job_status, message )
# End of main()

if __name__ == "__main__":
    # Argument menu / parsing
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--artifacts", type=str,
                        help="Name of the artifacts folder. Default: \"Artifacts\"", default=ARTIFACT_FOLDER)
    parser.add_argument("--slack_hook", type=str,
                        help="Slack hook URL for API calls. Example: \"https://hooks.slack.com/services/<id>/<id>/<id>\"", required=True)
    parser.add_argument("--slack_channel", type=str,
                        help="Comma separeted list with slack channel names. Example: \"Channel1,Channel-2\"", required=True)
    parser.add_argument("--pipeline", type=str,
                        help="Sets the pipeline type. Currently supported values: \"azure\" or \"jenkins\". Default: \"jenkins\"", default="")
    parser.add_argument("--job_name", type=str,
                        help="Name of the Job that will show up on the notification.", required=True)
    parser.add_argument("--job_dashboard_url", type=str,
                        help="URL for the run dashboard that will show up on the notification.", required=True)
    args = parser.parse_args()

    # Parse the artifact directory
    artifact_dir = args.artifacts
    # Parse Slack Hook
    slack_hook = args.slack_hook
    # Parse Slack Channel list
    slack_channels = args.slack_channel.split(',')
    # Parse Pipeline Type
    pipeline_type = args.pipeline
    # Parse Job Name
    job_name = args.job_name
    # Parse Job Dashboard URL
    job_url = args.job_dashboard_url

    # Calls the main script
    main(artifact_dir, slack_hook, slack_channels, pipeline_type, job_name, job_url)
