for /f "skip=1 tokens=3" %%s in ('query user administrator') do (
  %windir%\System32\tscon.exe %%s /dest:console
)