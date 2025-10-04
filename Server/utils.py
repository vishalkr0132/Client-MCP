def kill_port_process(port=8080):
    """Kill process using the specified port (Windows)"""
    try:
        import subprocess
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                pid = parts[-1]
                subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                print(f"Killed process {pid} using port {port}")
                return True
    except Exception as e:
        print(f"Error killing process: {e}")
    return False