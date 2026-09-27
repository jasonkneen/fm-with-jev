"""Jev picks one tool out of 40."""
import sys
from common import choice

TOOLS = dict(t.split(": ", 1) for t in """read_file: read a file
write_file: create or overwrite a file
edit_file: change part of a file
list_dir: list directory
grep: search file contents
glob: find files by name
run_shell: run a shell command
git_status: show git status
git_commit: commit changes
git_diff: show diff
create_pr: open a GitHub pull request
web_search: search the web
fetch_url: download a web page
send_email: send an email
read_email: read inbox
calendar_create: create calendar event
calendar_list: list upcoming events
slack_post: post a Slack message
slack_read: read a Slack channel
screenshot: capture the screen
click: click on screen
type_text: type keyboard text
open_app: launch a mac app
browser_open: open URL in browser
image_generate: generate an image
image_describe: describe an image
transcribe_audio: speech to text
text_to_speech: speak text aloud
translate: translate text
db_query: run SQL query
http_request: call an API
docker_run: run a container
kube_logs: read kubernetes pod logs
deploy_vercel: deploy to Vercel
weather: get weather forecast
maps_directions: get driving directions
memory_save: remember a fact
memory_search: recall saved facts
timer_set: set a timer
calculator: evaluate math""".splitlines())
QUERIES = ["commit my changes with message fix login", "why is my api pod crashlooping, check its logs",
           "remember that my dog is called Rex", "ship the frontend to production", "launch Figma"]
for q in ([sys.argv[1]] if len(sys.argv) > 1 else QUERIES):
    t, conf, ms = choice({"user_message": q}, TOOLS, "Pick the tool this request needs")
    print(f"{ms:5}ms  {t:16} p={conf:.2f}  {q}")
