import re, glob
pat = re.compile(r"[ \t]*\[cite:[^\]]*\]")
for f in glob.glob("docs/*.md") + glob.glob("resultados/*.md"):
    s = open(f, encoding="utf-8").read()
    n = len(pat.findall(s))
    if n:
        open(f, "w", encoding="utf-8", newline="\n").write(pat.sub("", s))
        print(f, n)