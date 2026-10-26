from .codes.check import CheckCommand
from .codes.info import InfoCommand
from .codes.list import ListCommand
from .receive.learn import LearnCommand
from .send.raw import RawCommand
from .send.send import SendCommand
from .signal.clean import CleanCommand
from .signal.frame import FrameCommand

# in the order of the help text
COMMANDS = (SendCommand, RawCommand, ListCommand, CheckCommand, InfoCommand, CleanCommand, FrameCommand, LearnCommand)
