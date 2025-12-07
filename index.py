import sys
import io

# Set stdout to UTF-8 to handle Japanese characters correctly
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("Content-type: text/html; charset=UTF-8\n")
print("""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Container Yard</title>
</head>
<body>
    <h1>Container Yard</h1>
    <p>Python CGI Script is running successfully.</p>
    <p>動作確認完了</p>
</body>
</html>
""")
