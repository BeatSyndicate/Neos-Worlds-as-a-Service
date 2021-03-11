import subprocess
import re
import time


def get_session_id():
    subprocess.check_call(["tmux", "send-keys", "-t", "neos", "\"sessionUrl\"", "ENTER"])
    subprocess.check_call(["tmux", "capture-pane", "-t", "neos"])
    buffer = subprocess.Popen(['tmux', 'show-buffer'], stdout=subprocess.PIPE).communicate()[0]
    buffer = buffer.decode('utf-8').split("\\n")
    buffer.reverse()
    buffer = '\n'.join(buffer)
    # example_test_session_id = 'S-adf3674c-a890-4574-875a-aed51e492921'
    regex_session_id = r'S-\w{8}-(\w{4}-){3}\w{12}'
    session_id = re.search(regex_session_id, buffer).group()
    return session_id


def neos_is_up():
    subprocess.check_call(["tmux", "send-keys", "-t", "neos", "\"status\"", "ENTER"])
    subprocess.check_call(["tmux", "capture-pane", "-t", "neos"])
    buffer = subprocess.Popen(['tmux', 'show-buffer'], stdout=subprocess.PIPE).communicate()[0]
    buffer = buffer.decode('utf-8').split("\\n")
    buffer.reverse()
    buffer = '\n'.join(buffer)
    if 'Uptime' in buffer:
        return True
    else:
        return False


if __name__ == "__main__":
    while not neos_is_up():
        print("waiting for neos...")
        time.sleep(3)
    print("neos is up!")
    try:
        print(get_session_id())
    except subprocess.CalledProcessError as e:
        raise Exception(e, "Tmux error, does 'tmux attach -t neos' work?")


