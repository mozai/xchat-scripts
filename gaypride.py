" This is an hexchat module "
# Python 3.x
import hexchat

# -- init
__module_name__ = "gaypride"
__module_version__ = "20161115"
__module_description__ = "rainbow text"
__module_author__ = "Mozai <moc.iazom@sesom>"

RAINBOW = [
  '\x0304', '\x0305', '\x0308', '\x0309', '\x0303',
  '\x0312', '\x0302', '\x0313', '\x0306']


def gaypride(word, word_eol, userdata):
  del(word, userdata)  # shut up pylint
  phrase = word_eol[1]
  j = len(phrase) // len(RAINBOW) + 1
  crumbs = [RAINBOW[i] + phrase[i * j:(i + 1) * j] for i in range(len(RAINBOW))]
  hexchat.command("say " + ''.join(crumbs))
  return hexchat.EAT_ALL
hexchat.hook_command('gay', gaypride, help='/gay something_fabulous')
hexchat.hook_command('pride', gaypride, help='/pride phrase to say in rainbow')

print("gaypride loaded (/gay, /pride)")
