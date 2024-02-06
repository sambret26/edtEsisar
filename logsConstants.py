from dotenv import load_dotenv
import os

load_dotenv()

# CONST

MAJ = os.environ.get('MAJ')
DB = os.environ.get('DB')
CAL = os.environ.get('CAL')

INFO = os.environ.get('INFO')
WARN = os.environ.get('WARN')
ERROR = os.environ.get('ERROR')
