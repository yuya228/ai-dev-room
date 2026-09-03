from pathlib import Path

helper = Path('.github/tmp-custom-github-issue-source.py')
src = helper.read_text(encoding='utf-8')

old_focusin = '''replace_once(
    "if(e.target===input||e.target===channelNameInput||e.target===channelDescInput||e.target===searchInput)",
    "if(e.target===input||e.target===channelNameInput||e.target===channelDescInput||e.target===channelSourceInput||e.target===searchInput)",
    'focusin source field',
)
'''
old_focusout = '''replace_once(
    "if(e.target===input||e.target===channelNameInput||e.target===channelDescInput||e.target===searchInput){viewportLockUntil=Date.now()+900;",
    "if(e.target===input||e.target===channelNameInput||e.target===channelDescInput||e.target===channelSourceInput||e.target===searchInput){viewportLockUntil=Date.now()+900;",
    'focusout source field',
)
'''
new_focus = '''old_focus = "if(e.target===input||e.target===channelNameInput||e.target===channelDescInput||e.target===searchInput)"
new_focus = "if(e.target===input||e.target===channelNameInput||e.target===channelDescInput||e.target===channelSourceInput||e.target===searchInput)"
focus_count = text.count(old_focus)
if focus_count != 2:
    raise SystemExit(f'focus fields: expected 2 targets, found {focus_count}')
text = text.replace(old_focus, new_focus)
'''

if old_focusin not in src or old_focusout not in src:
    raise SystemExit('temporary helper focus blocks not found')
src = src.replace(old_focusin, new_focus, 1).replace(old_focusout, '', 1)
exec(compile(src, str(helper), 'exec'))
